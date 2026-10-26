"""Playwright end-to-end tests against the sandbox project.

Every test module gets its own sandbox server with a freshly seeded database,
so the tests within a module can build on each other (like the old Cypress
specs) without leaking state into other modules. Run them in file order:

    uv run --group e2e pytest e2e -p no:randomly
"""

import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

ROOT = Path(__file__).resolve().parent.parent
MANAGE = ROOT / "sandbox" / "manage.py"
FIXTURES = [
    ROOT / "sandbox" / "exampledata" / name
    for name in ("users.json", "cms.json", "default_tags.json")
]


def sandbox_env():
    # pytest-django exports DJANGO_SETTINGS_MODULE for the unit tests.
    return {
        **os.environ,
        "ENVIRONMENT": "test",
        "DJANGO_SETTINGS_MODULE": "sandbox.settings",
    }


# Matches the old Cypress defaultCommandTimeout.
TIMEOUT = 8000


def manage(*args, cwd):
    subprocess.run(
        [sys.executable, str(MANAGE), *args], cwd=cwd, env=sandbox_env(), check=True
    )


@pytest.fixture(scope="session")
def seed_db(tmp_path_factory):
    path = tmp_path_factory.mktemp("seed")
    manage("migrate", "--verbosity", "0", cwd=path)
    manage("loaddata", "--verbosity", "0", *map(str, FIXTURES), cwd=path)
    return path / "db.sqlite3"


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def sandbox(seed_db, tmp_path_factory):
    """Start the sandbox with a fresh database and return its base URL."""
    path = tmp_path_factory.mktemp("sandbox")
    shutil.copy(seed_db, path / "db.sqlite3")
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    log = open(path / "runserver.log", "w")
    proc = subprocess.Popen(
        [sys.executable, str(MANAGE), "runserver", "--noreload", f"127.0.0.1:{port}"],
        cwd=path,
        env=sandbox_env(),
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    try:
        deadline = time.monotonic() + 60
        while True:
            try:
                urllib.request.urlopen(url, timeout=1)
                break
            except (urllib.error.URLError, ConnectionError):
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError(
                        "sandbox did not start:\n"
                        + (path / "runserver.log").read_text()
                    )
                time.sleep(0.2)
        yield url
    finally:
        proc.terminate()
        proc.wait()
        log.close()


@pytest.fixture(scope="module")
def admin_state(sandbox, browser, tmp_path_factory):
    """Log in to the Wagtail admin once per module and reuse the session."""
    context = browser.new_context(base_url=sandbox)
    page = context.new_page()
    page.goto("/cms/login/")
    page.fill("#id_username", "superuser")
    page.fill("#id_password", "testing")
    page.click("button[type='submit']")
    page.wait_for_url("**/cms/")
    # Keep only the admin session; every test starts without consent cookies.
    session = [c for c in context.cookies() if c["name"] in ("sessionid", "csrftoken")]
    context.clear_cookies()
    context.add_cookies(session)
    path = tmp_path_factory.mktemp("state") / "admin.json"
    context.storage_state(path=path)
    context.close()
    return path


@pytest.fixture
def context(new_context, sandbox, admin_state):
    context = new_context(base_url=sandbox, storage_state=admin_state)
    context.set_default_timeout(TIMEOUT)
    return context


@pytest.fixture(autouse=True)
def _expect_timeout():
    expect.set_options(timeout=TIMEOUT)


# Helpers


def set_wtm_cookie(page: Page, value):
    page.context.add_cookies(
        [{"name": "wtm", "value": value, "domain": "127.0.0.1", "path": "/"}]
    )


def get_cookie(page: Page, name):
    for cookie in page.context.cookies():
        if cookie["name"] == name:
            return cookie["value"]
    return None


def wait_for_cookie(page: Page, name, value):
    """Poll for a cookie value, like Cypress' retrying `getCookie().should()`."""
    deadline = time.monotonic() + TIMEOUT / 1000
    while True:
        current = get_cookie(page, name)
        if current == value or time.monotonic() > deadline:
            break
        page.wait_for_timeout(100)
    assert current == value


class ConsoleInfo:
    """Collects `console.info()` calls, replacing Cypress' console stub."""

    def __init__(self, page: Page):
        self.page = page
        self.messages = []
        page.on(
            "console", lambda msg: msg.type == "info" and self.messages.append(msg.text)
        )

    def reset(self):
        self.messages.clear()

    def wait_for(self, text):
        deadline = time.monotonic() + TIMEOUT / 1000
        while text not in self.messages and time.monotonic() < deadline:
            self.page.wait_for_timeout(100)
        assert text in self.messages, f"{text!r} not logged, got {self.messages}"

    def assert_not_called(self, text):
        assert text not in self.messages, f"{text!r} was logged"


@pytest.fixture
def console_info(page):
    return ConsoleInfo(page)


# Count (and swallow) `document.head.appendChild()` calls, like the Cypress
# `cy.stub(win.document.head, "appendChild")` did.
HEAD_APPEND_STUB = """
window.__headAppendChild = 0;
HTMLHeadElement.prototype.appendChild = function (node) {
  window.__headAppendChild += 1;
  return node;
};
"""


def assert_head_appends(page: Page, expected):
    """Visit the home page and wait for `expected` head.appendChild() calls."""
    page.add_init_script(HEAD_APPEND_STUB)
    page.goto("/")
    page.wait_for_function(
        "expected => window.__headAppendChild === expected", arg=expected
    )


def visit_and_get_wtm_cookie(page: Page, url="/"):
    """Visit `url` and return the `wtm` cookie set by the page response itself.

    Any later GET request with "pending" consent (e.g. the browser's favicon
    request) moves it on to "true", so read the value the document set.
    """
    response = page.goto(url)
    for header in response.headers_array():
        name, value = header["name"].lower(), header["value"]
        if name == "set-cookie" and value.startswith("wtm="):
            return value.split(";", 1)[0].removeprefix("wtm=").strip('"')
    return get_cookie(page, "wtm")


def publish(page: Page):
    """Publish the page open in the Wagtail editor (footer action menu)."""
    page.locator("footer .w-dropdown__toggle").click()
    page.locator("[name='action-publish']").click()
    expect(page.locator(".messages")).to_contain_text("has been published")
