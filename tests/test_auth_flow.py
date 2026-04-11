import pytest

from pages.login_page import LoginPage
from pages.tasks_page import TasksPage


def build_hash_url(base_url, fragment):
    clean_base_url = base_url.rstrip("/")
    clean_fragment = fragment.lstrip("/#")
    return f"{clean_base_url}/#/{clean_fragment}"


@pytest.mark.smoke
def test_login_page_elements(driver, base_url):
    page = LoginPage(driver)
    driver.get(base_url)

    assert page.is_username_input_visible(), "Поле Username не отображается"
    assert page.is_password_input_visible(), "Поле Password не отображается"
    assert page.is_login_button_visible(), "Кнопка логина не отображается"
    assert not page.is_profile_button_visible(), (
        "На странице логина не должна отображаться кнопка профиля"
    )


@pytest.mark.step_3
def test_login_form_validation(driver, base_url):
    page = LoginPage(driver)
    driver.get(base_url)

    page.click_submit()

    assert page.get_input_aria_invalid("username") == "true", (
        "Поле Username не помечено как невалидное"
    )
    assert page.get_input_aria_invalid("password") == "true", (
        "Поле Password не помечено как невалидное"
    )
    assert page.is_login_button_visible(), (
        "После невалидной отправки форма входа пропала"
    )


@pytest.mark.step_3
def test_successful_login_and_logout(driver, base_url):
    page = LoginPage(driver)
    driver.get(base_url)

    page.login("admin@google.com", "admin1234567")

    assert page.is_logged_in(), (
        "После логина не загрузилась защищенная часть приложения"
    )
    assert (
        driver.current_url.endswith("#/") or 
        driver.current_url == base_url
    ), "После логина приложение открыло неожиданный роут"

    tasks_page = TasksPage(driver)
    driver.get(build_hash_url(base_url, "tasks"))

    assert tasks_page.verify_filters_visible(), (
        "После логина не загрузилась страница tasks"
    )
    assert tasks_page.get_tasks_count() > 0, (
        "После логина на tasks не отображаются карточки"
    )

    page.logout()

    assert page.is_logged_out(), (
        "После логаута приложение не вернулось к экрану входа"
    )

    for protected_route in ("tasks", "users"):
        driver.get(build_hash_url(base_url, protected_route))

        assert page.is_logged_out(), (
            f"После logout доступ к роуту {protected_route} не закрыт"
        )


@pytest.mark.step_3
def test_burger_menu_and_dashboard(driver, base_url):
    page = LoginPage(driver)
    driver.get(base_url)

    page.login("admin@google.com", "admin1234567")

    assert page.is_dashboard_visible(), (
        "После логина не виден dashboard"
    )
    assert page.is_menu_open(), (
        "После логина боковое меню должно быть открыто"
    )

    page.toggle_menu()
    assert page.is_menu_closed(), "Бургер не закрыл меню"

    page.toggle_menu()
    assert page.is_menu_open(), "Бургер не открыл меню обратно"
    assert page.is_dashboard_visible(), (
        "После переключения меню пропал dashboard"
    )


@pytest.mark.step_3
def test_theme_toggle(driver, base_url):
    page = LoginPage(driver)
    driver.get(base_url)

    page.login("admin@google.com", "admin1234567")

    initial_icon = page.get_theme_icon_testid()

    page.toggle_theme()
    page.wait_for_theme_icon_change(initial_icon)
    toggled_icon = page.get_theme_icon_testid()

    assert toggled_icon != initial_icon, (
        "Переключение темы не изменило иконку темы"
    )

    page.toggle_theme()
    page.wait_for_theme_icon_change(toggled_icon)

    assert page.get_theme_icon_testid() == initial_icon, (
        "Повторное переключение темы не вернуло исходное состояние"
    )
