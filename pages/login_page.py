from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def login(self, username, password):
        self.wait.until(
            EC.visibility_of_element_located((By.NAME, "username"))
        ).send_keys(username)

        self.wait.until(
            EC.visibility_of_element_located((By.NAME, "password"))
        ).send_keys(password)

        self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[type="submit"]'))
        ).click()

        snackbar_locator = (By.CLASS_NAME, "MuiSnackbarContent-root")
        self.wait.until(EC.invisibility_of_element_located(snackbar_locator))

    def logout(self):
        self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[aria-label="Profile"]'))
        ).click()

        self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//li[contains(., 'Logout')]"))
        ).click()

    def is_login_button_visible(self):
        try:
            return self.wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'button[type="submit"]'))
            ).is_displayed()
        except TimeoutException:
            return False

    def is_username_input_visible(self):
        try:
            return self.wait.until(
                EC.visibility_of_element_located((By.NAME, "username"))
            ).is_displayed()
        except TimeoutException:
            return False

    def is_password_input_visible(self):
        try:
            return self.wait.until(
                EC.visibility_of_element_located((By.NAME, "password"))
            ).is_displayed()
        except TimeoutException:
            return False