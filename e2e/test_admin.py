import pytest
from playwright.sync_api import expect


def submit(page):
    page.locator(".actions button[type='submit']").click()


def edit_first(page):
    page.locator("[data-object-pk]").first.locator("a", has_text="Edit").click(
        force=True
    )


def delete_first(page):
    page.locator("[data-object-pk]").first.locator("a", has_text="Delete").click(
        force=True
    )
    page.locator("input[type='submit']").click()


def expect_first_name(page, name):
    expect(page.locator(".field-name_display").first).to_contain_text(name)


def expect_success(page, text):
    expect(page.locator(".messages .success")).to_contain_text(text)


def test_dashboard_shows_the_summary_panels(page):
    page.goto("/cms/")
    summary = page.locator(".w-summary__list")
    for label in (
        "Tags",
        "Constants",
        "Variables",
        "Triggers",
        "Cookie declarations",
        "Cookie consents",
    ):
        expect(summary).to_contain_text(label)


def test_cookie_bar_settings_change_title(page):
    page.goto("/cms/settings/wagtail_tag_manager/cookiebarsettings/1/")
    page.fill("#id_title", "We use cookies")
    submit(page)

    page.goto("/")
    expect(page.locator("#wtm_cookie_bar h4")).to_contain_text("We use cookies")


def test_cookie_bar_settings_reset_title(page):
    page.goto("/cms/settings/wagtail_tag_manager/cookiebarsettings/1/")
    page.fill("#id_title", "")
    submit(page)

    page.goto("/")
    expect(page.locator("#wtm_cookie_bar h4")).to_contain_text(
        "This website uses cookies"
    )


@pytest.mark.parametrize("model", ["tag", "constant", "variable"])
def test_close_the_help_block(page, model):
    page.goto(f"/cms/wagtail_tag_manager/{model}/")
    page.locator("#wtm_help_block a").click()
    expect(page.locator("#wtm_help_block")).not_to_be_visible()


# Tags


def test_create_tag(page):
    page.goto("/cms/wagtail_tag_manager/tag/")
    page.locator("a", has_text="Add tag").click()

    page.fill("#id_name", "A new tag")
    page.fill("#id_description", "Lorem ipsum")
    page.locator(".CodeMirror").click()
    page.keyboard.type("console.info('test')")
    submit(page)
    expect_first_name(page, "A new tag")


def test_update_tag(page):
    page.goto("/cms/wagtail_tag_manager/tag/")
    edit_first(page)
    page.fill("#id_name", "An updated tag")
    submit(page)
    expect_first_name(page, "An updated tag")


def test_tag_location_disabled_when_lazy(page):
    page.goto("/cms/wagtail_tag_manager/tag/")
    edit_first(page)
    page.select_option("#id_tag_loading", "lazy_load", force=True)
    expect(page.locator("input#id_tag_location")).to_have_value("0_top_head")
    expect(page.locator("select#id_tag_location")).to_be_disabled()


def test_delete_tag(page):
    page.goto("/cms/wagtail_tag_manager/tag/")
    delete_first(page)
    expect_success(page, "tag 'An updated tag' deleted.")


# Constants


def test_create_constant(page):
    page.goto("/cms/wagtail_tag_manager/constant/")
    page.locator("a", has_text="Add constant").click()

    page.fill("#id_name", "A new constant")
    page.fill("#id_description", "Lorem ipsum")
    page.fill("#id_key", "test")
    page.fill("#id_value", "Some cool test")
    submit(page)
    expect_first_name(page, "A new constant")


def test_use_constant(page):
    page.goto("/cms/wagtail_tag_manager/tag/create/")
    item = page.locator("[data-key='test']")
    item.scroll_into_view_if_needed()
    expect(item).to_contain_text("A new constant")


def test_update_constant(page):
    page.goto("/cms/wagtail_tag_manager/constant/")
    edit_first(page)
    page.fill("#id_name", "An updated constant")
    submit(page)
    expect_first_name(page, "An updated constant")


def test_delete_constant(page):
    page.goto("/cms/wagtail_tag_manager/constant/")
    delete_first(page)
    expect_success(page, "constant 'An updated constant' deleted.")


# Variables


def test_create_variable(page):
    page.goto("/cms/wagtail_tag_manager/variable/")
    page.locator("a", has_text="Add variable").click()

    page.fill("#id_name", "A new variable")
    page.fill("#id_description", "Lorem ipsum")
    page.fill("#id_key", "test")
    page.select_option("#id_variable_type", "_repath+", force=True)
    page.fill("#id_value", "/wtm/is/cool/")
    submit(page)
    expect_first_name(page, "A new variable")


def test_use_variable(page):
    page.goto("/cms/wagtail_tag_manager/tag/create/")
    item = page.locator("[data-key='test']")
    item.scroll_into_view_if_needed()
    expect(item).to_contain_text("A new variable")


def test_update_variable(page):
    page.goto("/cms/wagtail_tag_manager/variable/")
    edit_first(page)
    page.fill("#id_name", "An updated variable")
    page.select_option("#id_variable_type", "_cookie+", force=True)
    page.fill("#id_value", "wtm_id")
    submit(page)
    expect_first_name(page, "An updated variable")


def test_delete_variable(page):
    page.goto("/cms/wagtail_tag_manager/variable/")
    delete_first(page)
    expect_success(page, "variable 'An updated variable' deleted.")
