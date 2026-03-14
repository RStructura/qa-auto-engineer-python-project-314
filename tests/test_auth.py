import pytest
from selenium.webdriver.common.by import By


@pytest.mark.smoke
def test_login_page_renders(driver, base_url):
    driver.get(base_url)

    assert "Task manager" in driver.title

    username_input = driver.find_element(By.NAME, "username")
    assert username_input.is_displayed()

    password_input = driver.find_element(By.NAME, "password")
    assert password_input.is_displayed()

    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    assert login_button.is_enabled()
