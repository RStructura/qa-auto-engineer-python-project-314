# import time

import pytest
from selenium.webdriver.common.by import By

from pages.login_page import LoginPage


@pytest.mark.smoke
def test_login_page_elements(driver, base_url):
    driver.get(base_url)
    page = LoginPage(driver)

    # Ожидание загрузки заголовка
    page.wait.until(lambda d: "Task manager" in d.title)

    # Проверка наличия элементов
    assert "Task manager" in driver.title, "Заголовок страницы неверный"
    assert page.is_login_button_visible(), "Кнопка логина не отображается"
    assert page.is_username_input_visible(), "Поле Username не отображается"
    assert page.is_password_input_visible(), "Поле Password не отображается"
    assert page.is_login_button_visible(), "Кнопка логина не отображается"


@pytest.mark.step_3
def test_successful_login_and_logout(driver, base_url):
    page = LoginPage(driver)
    driver.get(base_url)
    # Авторизация
    page.login("admin@google.com", "admin1234567")
    # Проверка входа: поиск кнопки профиля
    assert driver.find_element(
        By.CSS_SELECTOR, 'button[aria-label="Profile"]').is_displayed()
    # Выход
    page.logout()
    # Проверка выхода: поиск кнопки логина
    assert page.is_login_button_visible()
    print("\nУспех! Вход и выход работают корректно.")
