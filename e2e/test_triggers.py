import pytest
from playwright.sync_api import expect

from .test_admin import (
    delete_first,
    edit_first,
    expect_first_name,
    expect_success,
    submit,
)


def test_close_the_help_block(page):
    page.goto("/cms/wagtail_tag_manager/trigger/")
    page.locator("#wtm_help_block a").click()
    expect(page.locator("#wtm_help_block")).not_to_be_visible()


def test_create_trigger(page):
    page.goto("/cms/wagtail_tag_manager/trigger/")
    page.locator("a", has_text="Add trigger").click()

    page.fill("#id_name", "A new trigger")
    page.fill("#id_description", "Lorem ipsum")
    page.locator("[value='9']").click(force=True)
    submit(page)
    expect_first_name(page, "A new trigger")


def test_update_trigger(page):
    page.goto("/cms/wagtail_tag_manager/trigger/")
    edit_first(page)
    page.fill("#id_name", "An updated trigger")
    submit(page)
    expect_first_name(page, "An updated trigger")


@pytest.mark.parametrize(
    "trigger_type, value",
    [
        ("history_change", None),
        ("javascript_error", None),
        ("click_all_elements", None),
        ("click_some_elements+", "input"),
        ("visibility_once_per_page+", "input"),
        ("visibility_once_per_element+", "input"),
        ("visibility_recurring+", "input"),
        ("scroll_vertical+", "5"),
        ("scroll_horizontal+", "5"),
        ("timer_timeout+", "100"),
        ("timer_interval+", "100"),
    ],
)
def test_update_trigger_type(page, trigger_type, value):
    page.goto("/cms/wagtail_tag_manager/trigger/")
    edit_first(page)
    page.select_option("#id_trigger_type", trigger_type)
    if value is not None:
        page.fill("#id_value", value)
    submit(page)
    expect_success(page, "Trigger 'An updated trigger' updated.")


def test_delete_trigger(page):
    page.goto("/cms/wagtail_tag_manager/trigger/")
    delete_first(page)
    expect_success(page, "trigger 'An updated trigger' deleted.")
