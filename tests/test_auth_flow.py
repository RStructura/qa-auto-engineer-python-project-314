import pytest
from selenium.webdriver.common.by import By

from pages.login_page import LoginPage


@pytest.mark.smoke
def test_login_page_elements(driver, base_url):
    driver.get(base_url)
    page = LoginPage(driver)
    # Проверка наличия элементов
    assert "Task manager" in driver.title
    assert page.is_login_button_visible(), "Кнопка логина не отображается"


@pytest.mark.step_3
def test_successful_login_and_logout(driver, base_url):
    page = LoginPage(driver)
    driver.get(base_url)
    # Авторизация
    page.login("test", "sadsads")
    # Проверка входа: поиск кнопки профиля
    assert driver.find_element(
        By.CSS_SELECTOR, 'button[aria-label="Profile"]').is_displayed()
    # Выход
    page.logout()
    # Проверка выхода: поиск кнопки логина
    assert page.is_login_button_visible()
    print("\nУспех! Вход и выход работают корректно.")
