from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base import BasePage


class LabelsPage(BasePage):
    route = "labels"

    def open_page(self) -> None:
        self.open(self.route)
        self.wait_for_list_or_empty()

    def wait_for_list_or_empty(self) -> None:
        self.wait.until(
            lambda d: (
                len(d.find_elements(By.CSS_SELECTOR, "table")) > 0
                or len(
                    d.find_elements(
                        By.CSS_SELECTOR,
                        ".RaEmpty-message",
                    )
                ) > 0
            )
        )

    def _label_locator(self, name: str):
        return (
            By.XPATH,
            "//td[contains(@class, 'column-name') "
            f"and normalize-space()='{name}']",
        )

    def wait_until_label_present(self, name: str) -> None:
        self.wait.until(
            lambda d: len(d.find_elements(*self._label_locator(name))) > 0
        )

    def wait_until_label_absent(self, name: str) -> None:
        self.wait.until(
            lambda d: len(d.find_elements(*self._label_locator(name))) == 0
        )

    def get_table(self):
        self.open_page()
        return self.wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "table"))
        )

    def create_label(self, name: str) -> bool:
        self.open_page()
        self.click_icon("Create")
        self.fill_input('input[name="name"]', name)
        self.click_icon("Save")
        self.open_page()
        try:
            self.wait_until_label_present(name)
            return True
        except TimeoutException:
            return False

    def edit_label(self, current_name: str, new_name: str) -> bool:
        self.open_page()
        self.safe_click(
            self.wait.until(
                EC.presence_of_element_located(
                    self._label_locator(current_name)
                )
            )
        )
        self.fill_input('input[name="name"]', new_name)
        self.click_icon("Save")
        self.open_page()
        try:
            self.wait_until_label_absent(current_name)
            self.wait_until_label_present(new_name)
            return True
        except TimeoutException:
            return False

    def delete_label(self, name: str) -> bool:
        self.open_page()
        self.safe_click(
            self.wait.until(
                EC.presence_of_element_located(self._label_locator(name))
            )
        )
        self.click_icon("Delete")
        self.open_page()
        try:
            self.wait_until_label_absent(name)
            return True
        except TimeoutException:
            return False

    def delete_all_labels(self) -> bool:
        self.open_page()
        rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        if not rows:
            return True

        checkbox = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "table thead tr th input[type='checkbox']",
                )
            )
        )
        self.safe_click(checkbox)
        self.click_icon("Delete")
        self.open_page()
        try:
            self.wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".RaEmpty-message")
                )
            )
            return True
        except TimeoutException:
            return False
