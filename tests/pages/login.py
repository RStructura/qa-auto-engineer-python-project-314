from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ..constants import DASHBOARD_TITLE
from .base import BasePage


class LoginPage(BasePage):
    def __init__(self, driver, base_url: str):
        super().__init__(driver, base_url)
        self.username_input = (By.NAME, "username")
        self.password_input = (By.NAME, "password")
        self.submit_button = (By.CSS_SELECTOR, 'button[type="submit"]')
        self.profile_button = (
            By.CSS_SELECTOR,
            'button[aria-label="Profile"]',
        )
        self.logout_item = (
            By.XPATH,
            "//li[@role='menuitem' and normalize-space()='Logout']",
        )
        self.dashboard_title = (
            By.XPATH,
            f"//*[normalize-space()='{DASHBOARD_TITLE}']",
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

    def login(self, username: str, password: str) -> None:
        self.open("login")
        self.wait.until(
            EC.visibility_of_element_located(self.username_input)
        ).send_keys(username)
        self.wait.until(
            EC.visibility_of_element_located(self.password_input)
        ).send_keys(password)
        self.safe_click(
            self.wait.until(
                EC.element_to_be_clickable(self.submit_button)
            )
        )
        self.wait.until(
            EC.visibility_of_element_located(self.dashboard_title)
        )
        self.wait.until(
            EC.visibility_of_element_located(self.profile_button)
        )

    def logout(self) -> None:
        self.open("tasks")
        self.safe_click(
            self.wait.until(
                EC.element_to_be_clickable(self.profile_button)
            )
        )
        self.safe_click(
            self.wait.until(
                EC.element_to_be_clickable(self.logout_item)
            )
        )
        self.wait.until(
            EC.visibility_of_element_located(self.submit_button)
        )

    def click_submit(self) -> None:
        self.safe_click(
            self.wait.until(
                EC.element_to_be_clickable(self.submit_button)
            )
        )

    def get_input_aria_invalid(self, field_name: str) -> str | None:
        return self.driver.find_element(
            By.NAME,
            field_name,
        ).get_attribute("aria-invalid")

    def is_login_button_visible(self) -> bool:
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.submit_button)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_username_input_visible(self) -> bool:
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.username_input)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_password_input_visible(self) -> bool:
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.password_input)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_profile_button_visible(self) -> bool:
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.profile_button)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_dashboard_visible(self) -> bool:
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.dashboard_title)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_menu_open(self) -> bool:
        return len(self.driver.find_elements(*self.menu_toggle_close)) > 0

    def is_menu_closed(self) -> bool:
        return len(self.driver.find_elements(*self.menu_toggle_open)) > 0

    def toggle_menu(self) -> None:
        if self.is_menu_open():
            self.safe_click(
                self.driver.find_element(*self.menu_toggle_close)
            )
            self.wait.until(
                lambda d: len(d.find_elements(*self.menu_toggle_open)) > 0
            )
            return

        if self.is_menu_closed():
            self.safe_click(
                self.driver.find_element(*self.menu_toggle_open)
            )
            self.wait.until(
                lambda d: len(d.find_elements(*self.menu_toggle_close)) > 0
            )
            return

        raise TimeoutException("Could not determine menu state")

    def toggle_theme(self) -> None:
        self.safe_click(
            self.wait.until(
                EC.element_to_be_clickable(self.theme_toggle)
            )
        )

    def get_theme_icon_testid(self) -> str:
        if len(self.driver.find_elements(*self.brightness7_icon)) > 0:
            return "Brightness7Icon"
        if len(self.driver.find_elements(*self.brightness4_icon)) > 0:
            return "Brightness4Icon"
        raise TimeoutException("Theme icon not found")

    def wait_for_theme_icon_change(self, previous_icon: str) -> None:
        self.wait.until(
            lambda _d: self.get_theme_icon_testid() != previous_icon
        )

    def is_logged_in(self) -> bool:
        return self.is_profile_button_visible() and self.is_dashboard_visible()

    def is_logged_out(self) -> bool:
        return (
            not self.is_profile_button_visible()
            and self.is_login_button_visible()
            and self.is_username_input_visible()
            and self.is_password_input_visible()
        )
