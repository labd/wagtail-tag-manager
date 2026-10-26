from .conftest import publish, set_wtm_cookie

ALL = "necessary:true|preferences:true|statistics:true|marketing:true"
PASSIVE = [
    "Lazy passive required",
    "Lazy passive initial",
    "Lazy passive delayed",
    "Lazy passive regular",
]


def toggle_passive_tags(page):
    page.goto("/cms/pages/2/edit/")
    page.locator("a[href='#tab-settings']").click()
    for label in PASSIVE:
        page.get_by_text(label, exact=True).click()
    publish(page)


def visit(page, console_info, cookie):
    set_wtm_cookie(page, cookie)
    console_info.reset()
    page.goto("/")
    page.wait_for_load_state("networkidle")


def test_can_enable_page_tags(page, console_info):
    toggle_passive_tags(page)

    visit(page, console_info, ALL)
    for label in PASSIVE:
        console_info.wait_for(label.lower())


def test_will_honor_consent(page, console_info):
    visit(
        page,
        console_info,
        "necessary:true|preferences:unset|statistics:unset|marketing:false",
    )
    console_info.wait_for("lazy passive required")
    console_info.wait_for("lazy passive initial")
    console_info.assert_not_called("lazy passive delayed")
    console_info.assert_not_called("lazy passive regular")

    visit(
        page,
        console_info,
        "necessary:false|preferences:false|statistics:delayed|marketing:false",
    )
    console_info.wait_for("lazy passive required")
    console_info.assert_not_called("lazy passive initial")
    console_info.assert_not_called("lazy passive delayed")
    console_info.assert_not_called("lazy passive regular")


def test_can_disable_page_tags(page, console_info):
    toggle_passive_tags(page)

    visit(page, console_info, ALL)
    for label in PASSIVE:
        console_info.assert_not_called(label.lower())
