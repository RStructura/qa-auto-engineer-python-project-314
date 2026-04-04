from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        self.username_input = (By.NAME, "username")
        self.password_input = (By.NAME, "password")
        self.submit_button = (By.CSS_SELECTOR, 'button[type="submit"]')
        self.profile_button = (
            By.CSS_SELECTOR,
            'button[aria-label="Profile"]',
        )
        self.logout_item = (By.XPATH, "//li[contains(., 'Logout')]")

    def login(self, username, password):
        username_input = self.wait.until(
            EC.visibility_of_element_located(self.username_input)
        )
        username_input.clear()
        username_input.send_keys(username)

        password_input = self.wait.until(
            EC.visibility_of_element_located(self.password_input)
        )
        password_input.clear()
        password_input.send_keys(password)

        self.wait.until(
            EC.element_to_be_clickable(self.submit_button)
        ).click()

        self.wait.until(
            lambda d: (
                len(d.find_elements(*self.profile_button)) > 0
                and d.find_element(*self.profile_button).is_displayed()
            )
        )
        self.wait.until(
            EC.invisibility_of_element_located(self.submit_button)
        )

    def logout(self):
        self.wait.until(
            EC.element_to_be_clickable(self.profile_button)
        ).click()
        self.wait.until(
            EC.element_to_be_clickable(self.logout_item)
        ).click()

        self.wait.until(
            EC.visibility_of_element_located(self.submit_button)
        )
        self.wait.until(
            lambda d: len(d.find_elements(*self.profile_button)) == 0
        )

    def is_login_button_visible(self):
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.submit_button)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_username_input_visible(self):
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.username_input)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_password_input_visible(self):
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.password_input)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_profile_button_visible(self):
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.profile_button)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_logged_in(self):
        return (
            self.is_profile_button_visible()
            and not self.is_login_button_visible()
            and not self.is_username_input_visible()
            and not self.is_password_input_visible()
        )

    def is_logged_out(self):
        return (
            not self.is_profile_button_visible()
            and self.is_login_button_visible()
            and self.is_username_input_visible()
            and self.is_password_input_visible()
        )
