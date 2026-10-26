import re

import pytest
from playwright.sync_api import expect

from .conftest import get_cookie, set_wtm_cookie, wait_for_cookie

HIDDEN = re.compile(r"\bhidden\b")


def submit(page, *toggle):
    bar = page.locator("#wtm_cookie_bar")
    expect(bar).to_be_visible()
    for name in toggle:
        bar.locator(f"input#id_{name}").click()
    bar.locator("input[type='submit']").click()
    expect(bar).to_have_class(HIDDEN)
    expect(bar).not_to_be_visible()


@pytest.mark.parametrize(
    "toggle, expected",
    [
        ((), "necessary:true|preferences:true|statistics:true|marketing:false"),
        (
            ("preferences", "statistics"),
            "necessary:true|preferences:false|statistics:false|marketing:false",
        ),
        (
            ("statistics",),
            "necessary:true|preferences:true|statistics:false|marketing:false",
        ),
        (
            ("preferences",),
            "necessary:true|preferences:false|statistics:true|marketing:false",
        ),
        (
            ("preferences", "statistics", "marketing"),
            "necessary:true|preferences:false|statistics:false|marketing:true",
        ),
        (
            ("marketing",),
            "necessary:true|preferences:true|statistics:true|marketing:true",
        ),
    ],
    ids=["default", "necessary", "preferences", "statistics", "marketing", "all"],
)
def test_save_cookies(page, toggle, expected):
    page.goto("/")
    submit(page, *toggle)
    wait_for_cookie(page, "wtm", expected)
    assert get_cookie(page, "wtm_id")


@pytest.mark.parametrize(
    "value",
    [
        "necessary:true|preferences:unset|statistics:false|marketing:false",
        "necessary:true|preferences:false|statistics:unset|marketing:false",
    ],
    ids=["preferences-unset", "statistics-unset"],
)
def test_displayed_when_unset(page, value):
    set_wtm_cookie(page, value)
    page.goto("/")
    bar = page.locator("#wtm_cookie_bar")
    expect(bar).not_to_have_class(HIDDEN)
    expect(bar).to_be_visible()


@pytest.mark.parametrize(
    "value",
    [
        "necessary:true|preferences:false|statistics:false|marketing:false",
        "necessary:true|preferences:true|statistics:true|marketing:true",
    ],
    ids=["all-false", "all-true"],
)
def test_hidden_when_decided(page, value):
    set_wtm_cookie(page, value)
    page.goto("/")
    bar = page.locator("#wtm_cookie_bar")
    expect(bar).to_have_class(HIDDEN)
    expect(bar).not_to_be_visible()


def test_manage_link(page):
    page.goto("/")
    page.locator("#wtm_cookie_bar .manage-link a").click()
    expect(page).to_have_url(re.compile("/wtm/manage/"))
