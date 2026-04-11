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
        self.dashboard_title = (
            By.XPATH,
            "//*[normalize-space()='Welcome to the administration']",
        )
        self.menu_toggle_open = (
            By.CSS_SELECTOR,
            'button[aria-label="Open menu"]',
        )
        self.menu_toggle_close = (
            By.CSS_SELECTOR,
            'button[aria-label="Close menu"]',
        )
        self.theme_toggle = (
            By.CSS_SELECTOR,
            'button[aria-label="Toggle light/dark mode"]',
        )
        self.brightness7_icon = (
            By.CSS_SELECTOR,
            '[data-testid="Brightness7Icon"]',
        )
        self.brightness4_icon = (
            By.CSS_SELECTOR,
            '[data-testid="Brightness4Icon"]',
        )

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
            EC.visibility_of_element_located(self.dashboard_title)
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

    def click_submit(self):
        self.wait.until(
            EC.element_to_be_clickable(self.submit_button)
        ).click()

    def get_input_aria_invalid(self, field_name):
        return self.driver.find_element(
            By.NAME,
            field_name,
        ).get_attribute("aria-invalid")

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

    def is_dashboard_visible(self):
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.dashboard_title)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_menu_open(self):
        return len(self.driver.find_elements(*self.menu_toggle_close)) > 0

    def is_menu_closed(self):
        return len(self.driver.find_elements(*self.menu_toggle_open)) > 0

    def toggle_menu(self):
        if self.is_menu_open():
            self.driver.find_element(*self.menu_toggle_close).click()
            self.wait.until(
                lambda d: len(d.find_elements(*self.menu_toggle_open)) > 0
            )
            return

        if self.is_menu_closed():
            self.driver.find_element(*self.menu_toggle_open).click()
            self.wait.until(
                lambda d: len(d.find_elements(*self.menu_toggle_close)) > 0
            )
            return

        raise TimeoutException("Не удалось определить состояние меню")

    def open_profile_menu(self):
        self.wait.until(
            EC.element_to_be_clickable(self.profile_button)
        ).click()

    def toggle_theme(self):
        self.wait.until(
            EC.element_to_be_clickable(self.theme_toggle)
        ).click()

    def get_theme_icon_testid(self):
        if len(self.driver.find_elements(*self.brightness7_icon)) > 0:
            return "Brightness7Icon"
        if len(self.driver.find_elements(*self.brightness4_icon)) > 0:
            return "Brightness4Icon"
        raise TimeoutException("Иконка темы не найдена")

    def wait_for_theme_icon_change(self, previous_icon):
        self.wait.until(
            lambda _d: self.get_theme_icon_testid() != previous_icon
        )

    def is_logged_in(self):
        return self.is_profile_button_visible() and self.is_dashboard_visible()

    def is_logged_out(self):
        return (
            not self.is_profile_button_visible()
            and self.is_login_button_visible()
            and self.is_username_input_visible()
            and self.is_password_input_visible()
        )
