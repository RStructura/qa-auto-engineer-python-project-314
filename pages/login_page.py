from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def login(self, username, password):
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

    def logout(self):
        self.driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label="Profile"]').click()
        self.driver.find_element(
            By.XPATH, "//li[contains(., 'Logout')]").click()

    def is_login_button_visible(self):
        try:
            return self.driver.find_element(
                By.CSS_SELECTOR, 'button[type="submit"]').is_displayed()
        except NoSuchElementException:
            return False





