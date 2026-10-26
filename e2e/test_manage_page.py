import re

import pytest
from playwright.sync_api import expect

from .conftest import get_cookie, wait_for_cookie


def test_has_a_form(page):
    page.goto("/wtm/manage/")

    form = page.locator("form:not(.form)")
    form.scroll_into_view_if_needed()
    expect(form).to_have_attribute("method", "POST")
    expect(form).to_have_attribute("action", "/wtm/manage/")

    checkboxes = form.locator("input[type='checkbox']")
    expect(checkboxes).to_have_count(4)
    expect(checkboxes.nth(0)).to_be_disabled()
    expect(checkboxes.nth(1)).to_be_checked()
    expect(checkboxes.nth(2)).to_be_checked()
    expect(checkboxes.nth(3)).not_to_be_checked()


def test_no_visible_cookie_bar(page):
    # The bar is rendered hidden and only shown by the client script when
    # consent is still undecided (the old Cypress check ran before that
    # script). On the manage page it never links to the manage page itself.
    response = page.goto("/wtm/manage/")
    tag = re.search(r'<div[^>]*id="wtm_cookie_bar"[^>]*>', response.text()).group(0)
    assert re.search(r'class="[^"]*\bhidden\b', tag), tag
    expect(page.locator("#wtm_cookie_bar .manage-link")).to_have_count(0)


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
    page.goto("/wtm/manage/")
    form = page.locator("form:not(.form)")
    form.scroll_into_view_if_needed()
    for name in toggle:
        form.locator(f"input#id_{name}").click()
    form.locator("input[type='submit']").click()

    wait_for_cookie(page, "wtm", expected)
    assert get_cookie(page, "wtm_id")
