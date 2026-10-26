from .conftest import (
    assert_head_appends,
    set_wtm_cookie,
    visit_and_get_wtm_cookie,
)

NECESSARY_ONLY = "necessary:true|preferences:false|statistics:false|marketing:false"


def visit(page, console_info):
    console_info.reset()
    page.goto("/")
    page.wait_for_load_state("networkidle")


# Necessary tags


def test_necessary_will_be_loaded(page, console_info):
    set_wtm_cookie(page, NECESSARY_ONLY)
    visit(page, console_info)
    console_info.wait_for("instant required")
    console_info.wait_for("lazy required")


def test_necessary_will_always_be_loaded(page, console_info):
    console_info.reset()
    assert (
        visit_and_get_wtm_cookie(page)
        == "necessary:true|preferences:unset|statistics:pending|marketing:false"
    )
    console_info.wait_for("instant required")
    console_info.wait_for("lazy required")

    for value in (
        "necessary:false|preferences:false|statistics:false|marketing:false",
        "necessary:unset|preferences:false|statistics:false|marketing:false",
    ):
        set_wtm_cookie(page, value)
        console_info.reset()
        assert visit_and_get_wtm_cookie(page) == NECESSARY_ONLY
        console_info.wait_for("instant required")
        console_info.wait_for("lazy required")


def test_necessary_will_be_loaded_instantly_and_lazy(page):
    set_wtm_cookie(page, NECESSARY_ONLY)
    assert_head_appends(page, 1)


# Preference tags


def test_preferences_will_be_loaded(page, console_info):
    set_wtm_cookie(
        page, "necessary:true|preferences:unset|statistics:false|marketing:false"
    )
    visit(page, console_info)
    console_info.wait_for("instant initial")
    console_info.wait_for("lazy initial")


def test_preferences_will_not_be_loaded(page, console_info):
    set_wtm_cookie(page, NECESSARY_ONLY)
    visit(page, console_info)
    console_info.assert_not_called("instant initial")
    console_info.assert_not_called("lazy initial")


def test_preferences_will_be_loaded_lazy(page):
    set_wtm_cookie(
        page, "necessary:true|preferences:unset|statistics:false|marketing:false"
    )
    assert_head_appends(page, 3)


def test_preferences_will_be_loaded_instantly_and_lazy(page):
    set_wtm_cookie(
        page, "necessary:true|preferences:true|statistics:false|marketing:false"
    )
    assert_head_appends(page, 2)


# Statistical tags


def test_statistics_will_be_loaded_at_the_second_visit(page, console_info):
    # The Cypress spec checked the preference ("initial") tags here, which are
    # loaded on the first visit as well; statistics ("delayed") tags are the
    # ones that wait for the second visit.
    visit(page, console_info)
    console_info.assert_not_called("instant delayed")
    console_info.assert_not_called("lazy delayed")

    console_info.reset()
    page.reload()
    console_info.wait_for("instant delayed")
    console_info.wait_for("lazy delayed")


def test_statistics_will_not_be_loaded_at_the_second_visit(page, console_info):
    set_wtm_cookie(page, NECESSARY_ONLY)
    for _ in range(2):
        visit(page, console_info)
        console_info.assert_not_called("instant delayed")
        console_info.assert_not_called("lazy delayed")


def test_statistics_will_be_loaded_lazy(page):
    set_wtm_cookie(
        page, "necessary:true|preferences:unset|statistics:false|marketing:false"
    )
    assert_head_appends(page, 3)


def test_statistics_will_be_loaded_instantly_and_lazy(page):
    set_wtm_cookie(
        page, "necessary:true|preferences:true|statistics:false|marketing:false"
    )
    assert_head_appends(page, 2)


# Marketing tags


def test_marketing_cant_be_unset(page):
    set_wtm_cookie(
        page, "necessary:true|preferences:false|statistics:false|marketing:unset"
    )
    assert visit_and_get_wtm_cookie(page) == NECESSARY_ONLY


def test_marketing_will_not_be_loaded(page, console_info):
    set_wtm_cookie(page, NECESSARY_ONLY)
    visit(page, console_info)
    console_info.assert_not_called("instant regular")
    console_info.assert_not_called("lazy regular")


def test_marketing_will_be_loaded(page, console_info):
    set_wtm_cookie(
        page, "necessary:true|preferences:false|statistics:false|marketing:true"
    )
    visit(page, console_info)
    console_info.wait_for("instant regular")
    console_info.wait_for("lazy regular")


def test_marketing_will_be_loaded_instantly_and_lazy(page):
    set_wtm_cookie(
        page, "necessary:true|preferences:false|statistics:false|marketing:true"
    )
    assert_head_appends(page, 2)
