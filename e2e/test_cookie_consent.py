from playwright.sync_api import expect

from .conftest import get_cookie, publish, visit_and_get_wtm_cookie, wait_for_cookie

CONSENT_SETTINGS = "/cms/settings/wagtail_tag_manager/cookieconsentsettings/1/"
DEFAULT = "necessary:true|preferences:true|statistics:true|marketing:false"


def register_consent(page):
    page.goto("/")
    page.locator("#wtm_cookie_bar input[type='submit']").click()
    wait_for_cookie(page, "wtm", DEFAULT)
    assert get_cookie(page, "wtm_id")


def change_homepage(page):
    page.goto("/cms/pages/2/edit/")
    publish(page)


def test_consent_will_be_registered(page):
    page.goto("/")
    bar = page.locator("#wtm_cookie_bar")
    expect(bar).to_be_visible()
    bar.locator("input#id_marketing").click()
    bar.locator("input[type='submit']").click()
    wait_for_cookie(
        page, "wtm", "necessary:true|preferences:true|statistics:true|marketing:true"
    )

    page.goto("/cms/reports/cookie-consent/")
    # The report is a Wagtail ReportView now; the identifier is the first column.
    first_row = page.locator(".listing tbody tr").first
    expect(first_row.locator("td").first).to_contain_text(get_cookie(page, "wtm_id"))


def test_consent_will_be_invalidated(page):
    # Configure condition page
    page.goto(CONSENT_SETTINGS)
    page.locator("button[data-chooser-action-choose]").first.click(force=True)
    expect(page.locator(".modal-content")).to_be_visible()
    page.locator("a[data-title='Wagtail Tag Manager']").first.click(force=True)
    page.locator(".actions button[type='submit']").click()

    register_consent(page)
    change_homepage(page)

    assert (
        visit_and_get_wtm_cookie(page)
        == "necessary:true|preferences:unset|statistics:pending|marketing:false"
    )


def test_consent_will_not_be_invalidated(page):
    # Remove condition page
    page.goto(CONSENT_SETTINGS)
    page.locator("button[aria-label='Actions']").click(force=True)
    page.locator("button[data-chooser-action-clear]").click(force=True)
    page.locator(".actions button[type='submit']").click()

    register_consent(page)
    change_homepage(page)

    assert visit_and_get_wtm_cookie(page) == DEFAULT
