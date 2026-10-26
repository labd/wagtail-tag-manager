from playwright.sync_api import expect

from .conftest import visit_and_get_wtm_cookie


def test_website_contains_base_configuration(page):
    assert (
        visit_and_get_wtm_cookie(page)
        == "necessary:true|preferences:unset|statistics:pending|marketing:false"
    )

    body = page.locator("body")
    expect(body).to_have_attribute("data-wtm-config", "/wtm/config/")
    expect(body).to_have_attribute("data-wtm-lazy", "/wtm/lazy/")

    expect(
        page.locator("link[href='/static/wagtail_tag_manager/wtm.bundle.css']")
    ).to_have_count(1)
    expect(
        page.locator("script[src='/static/wagtail_tag_manager/wtm.bundle.js']")
    ).to_have_count(1)


def test_website_has_a_configured_cookie_bar(page):
    page.goto("/")

    bar = page.locator("#wtm_cookie_bar")
    expect(bar).to_be_visible()
    expect(bar).to_have_class("cleanslate")
    expect(bar).to_contain_text("This website uses cookies")

    form = bar.locator("form")
    expect(form).to_have_class("form")
    expect(form).to_have_attribute("method", "POST")
    expect(form).to_have_attribute("action", "/wtm/manage/")

    checkboxes = form.locator("input[type='checkbox']")
    expect(checkboxes).to_have_count(4)
    expect(checkboxes.nth(0)).to_be_disabled()
    expect(checkboxes.nth(1)).to_be_checked()
    expect(checkboxes.nth(2)).to_be_checked()
    expect(checkboxes.nth(3)).not_to_be_checked()

    link = bar.locator(".manage-link a")
    expect(link).to_have_attribute("href", "/wtm/manage/")
    expect(link).to_contain_text("Manage settings")

    expect(bar.locator("input[type='submit']")).to_have_value("Save")


def test_api_returns_a_valid_config(page):
    with page.expect_response(lambda r: "/wtm/config/" in r.url) as response:
        page.goto("/")
    assert response.value.status == 200


def test_api_returns_a_valid_lazy_state(page):
    with page.expect_response(
        lambda r: r.url.endswith("/wtm/lazy/") and r.request.method == "POST"
    ) as response:
        page.goto("/")
    assert response.value.status == 200
