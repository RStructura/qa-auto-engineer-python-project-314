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

    print("\nУспех! Все основные элементы отображаются корректно")


@pytest.mark.step_3
def test_successful_login_and_logout(driver, base_url):
    page = LoginPage(driver)
    driver.get(base_url)

    page.login("admin@google.com", "admin1234567")

    assert page.is_profile_button_visible(), (
        "После логина не отображается кнопка профиля"
    )
    assert not page.is_login_button_visible(), (
        "После логина кнопка входа не должна быть видна"
    )
    assert not page.is_username_input_visible(), (
        "После логина поле Username не должно быть видно"
    )
    assert not page.is_password_input_visible(), (
        "После логина поле Password не должно быть видно"
    )

    page.logout()

    assert page.is_login_button_visible(), (
        "После логаута кнопка входа должна быть видна"
    )
    assert page.is_username_input_visible(), (
        "После логаута поле Username должно быть видно"
    )
    assert page.is_password_input_visible(), (
        "После логаута поле Password должно быть видно"
    )
    assert not page.is_profile_button_visible(), (
        "После логаута кнопка профиля не должна отображаться"
    )

    print("\nУспех! Вход и выход работают корректно.")
