from __future__ import annotations

from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..constants import DEFAULT_TIMEOUT
from ..utils.text import build_xpath_by_text


class BasePage:
    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    def open(self, fragment: str = "") -> None:
        fragment = fragment.lstrip("/")
        if fragment and not fragment.startswith("#/"):
            fragment = f"#/{fragment}"

        url = f"{self.base_url}/{fragment}" if fragment else self.base_url
        self.driver.get(url)

    def safe_click(self, element) -> None:
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element,
        )
        try:
            element.click()
        except WebDriverException:
            self.driver.execute_script("arguments[0].click();", element)

    def wait_for_text(self, text: str, tag: str = "*"):
        locator = (By.XPATH, build_xpath_by_text(tag, text))
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click_by_text(self, text: str, tag: str = "*"):
        element = self.wait_for_text(text, tag)
        self.safe_click(element)
        return element

    def click_icon(self, aria_label: str):
        locator = (By.CSS_SELECTOR, f'[aria-label="{aria_label}"]')
        element = self.wait.until(EC.presence_of_element_located(locator))
        self.safe_click(element)
        return element

    def clear_input(self, selector: str):
        field = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        self.safe_click(field)
        field.send_keys(Keys.CONTROL, "a")
        field.send_keys(Keys.DELETE)

        self.driver.execute_script(
            (
                "if (arguments[0].value !== '') {"
                "  arguments[0].value = '';"
                "}"
                "arguments[0].dispatchEvent("
                "  new Event('input', { bubbles: true })"
                ");"
                "arguments[0].dispatchEvent("
                "  new Event('change', { bubbles: true })"
                ");"
            ),
            field,
        )

        self.wait.until(
            lambda _d: (field.get_attribute("value") or "") == ""
        )
        return field

    def fill_input(self, selector: str, value: str):
        field = self.clear_input(selector)
        if value:
            field.send_keys(value)
        return field

    def select_from_dropdown(self, selector: str, item_text: str):
        element = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

        trigger = element
        if element.tag_name.lower() == "input":
            try:
                trigger = element.find_element(
                    By.XPATH,
                    "./parent::*//*[@role='combobox']",
                )
            except NoSuchElementException:
                trigger = element

        self.safe_click(trigger)

        option_locator = (By.XPATH, build_xpath_by_text("li", item_text))
        option = self.wait.until(
            EC.visibility_of_element_located(option_locator)
        )
        self.safe_click(option)
        return option
