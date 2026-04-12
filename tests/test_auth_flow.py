import pytest

from .constants import USER
from .pages.login import LoginPage
from .pages.tasks import TasksPage


def build_hash_url(base_url: str, fragment: str) -> str:
    clean_base_url = base_url.rstrip("/")
    clean_fragment = fragment.lstrip("/#")
    return f"{clean_base_url}/#/{clean_fragment}"


@pytest.mark.smoke
def test_login_page_elements(driver, base_url):
    page = LoginPage(driver, base_url)
    driver.get(base_url)

    assert page.is_username_input_visible(), (
        "Username input is not visible"
    )
    assert page.is_password_input_visible(), (
        "Password input is not visible"
    )
    assert page.is_login_button_visible(), (
        "Sign in button is not visible"
    )
    assert not page.is_profile_button_visible(), (
        "Profile button must be hidden on login page"
    )


@pytest.mark.step_3
def test_login_form_validation(driver, base_url):
    page = LoginPage(driver, base_url)
    driver.get(base_url)

    page.click_submit()

    assert page.get_input_aria_invalid("username") == "true", (
        "Username field is not marked invalid"
    )
    assert page.get_input_aria_invalid("password") == "true", (
        "Password field is not marked invalid"
    )
    assert page.is_login_button_visible(), (
        "Login form disappeared after invalid submit"
    )


@pytest.mark.step_3
def test_successful_login_and_logout(driver, base_url):
    page = LoginPage(driver, base_url)
    driver.get(base_url)

    page.login(USER["login"], USER["password"])

    assert page.is_logged_in(), (
        "Protected app shell did not load after login"
    )
    assert (
        driver.current_url.endswith("#/")
        or driver.current_url == base_url
    ), "Unexpected route after login"

    tasks_page = TasksPage(driver, base_url)
    driver.get(build_hash_url(base_url, "tasks"))

    assert tasks_page.verify_filters_visible(), (
        "Tasks page did not load after login"
    )

    page.logout()

    assert page.is_logged_out(), (
        "App did not return to login screen after logout"
    )

    for protected_route in ("tasks", "users"):
        driver.get(build_hash_url(base_url, protected_route))
        assert page.is_logged_out(), (
            f"Protected route {protected_route} is still accessible"
        )


@pytest.mark.step_3
def test_burger_menu_and_dashboard(driver, base_url):
    page = LoginPage(driver, base_url)
    driver.get(base_url)

    page.login(USER["login"], USER["password"])

    assert page.is_dashboard_visible(), "Dashboard is not visible"
    assert page.is_menu_open(), "Side menu should be open after login"

    page.toggle_menu()
    assert page.is_menu_closed(), "Burger did not close menu"

    page.toggle_menu()
    assert page.is_menu_open(), "Burger did not reopen menu"
    assert page.is_dashboard_visible(), (
        "Dashboard disappeared after menu toggling"
    )


@pytest.mark.step_3
def test_theme_toggle(driver, base_url):
    page = LoginPage(driver, base_url)
    driver.get(base_url)

    page.login(USER["login"], USER["password"])

    initial_icon = page.get_theme_icon_testid()

    page.toggle_theme()
    page.wait_for_theme_icon_change(initial_icon)
    toggled_icon = page.get_theme_icon_testid()

    assert toggled_icon != initial_icon, (
        "Theme toggle did not change theme icon"
    )

    page.toggle_theme()
    page.wait_for_theme_icon_change(toggled_icon)

    assert page.get_theme_icon_testid() == initial_icon, (
        "Theme toggle did not restore original state"
    )
