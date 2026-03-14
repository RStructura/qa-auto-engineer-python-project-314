import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.login_page import LoginPage


def test_successful_login_and_logout(driver, base_url):
    login_page = LoginPage(driver)
    driver.get(base_url)

    login_page.login("test", "123456")

    wait = WebDriverWait(driver, 10)
    dashboard_element = wait.until(
        EC.presence_of_element_located((By.ID, "main-content"))
    )
    assert dashboard_element.is_displayed()

    login_page.logout()

    wait.until(
        EC.visibility_of_element_located(login_page.login_button)
    )
    assert driver.find_element(*login_page.login_button).is_displayed()
