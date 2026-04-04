import pytest

from pages.login_page import LoginPage


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
def test_successful_login_and_logout(driver, base_url):
    page = LoginPage(driver)
    driver.get(base_url)

    page.login("admin@google.com", "admin1234567")
    assert page.is_logged_in(), (
        "После логина приложение осталось в состоянии login"
    )

    page.logout()
    assert page.is_logged_out(), (
        "После логаута приложение не вернулось к экрану входа"
    )
