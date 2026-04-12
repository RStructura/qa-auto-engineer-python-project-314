from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base import BasePage


class StatusesPage(BasePage):
    route = "task_statuses"

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

    def _status_locator(self, name: str):
        return (
            By.XPATH,
            "//td[contains(@class, 'column-name') "
            f"and normalize-space()='{name}']",
        )

    def wait_until_status_present(self, name: str) -> None:
        self.wait.until(
            lambda d: len(d.find_elements(*self._status_locator(name))) > 0
        )

    def wait_until_status_absent(self, name: str) -> None:
        self.wait.until(
            lambda d: len(d.find_elements(*self._status_locator(name))) == 0
        )

    def get_table(self):
        self.open_page()
        return self.wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "table"))
        )

    def get_status_row_values(self, name: str) -> dict[str, str]:
        self.open_page()
        row = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//tr[.//td[contains(@class, 'column-name') "
                    f"and normalize-space()='{name}']]",
                )
            )
        )
        return {
            "name": row.find_element(
                By.CSS_SELECTOR,
                "td.column-name",
            ).text.strip(),
            "slug": row.find_element(
                By.CSS_SELECTOR,
                "td.column-slug",
            ).text.strip(),
        }

    def create_status(self, name: str, slug: str) -> bool:
        self.open_page()
        self.click_icon("Create")
        self.fill_input('input[name="name"]', name)
        self.fill_input('input[name="slug"]', slug)
        self.click_icon("Save")
        self.open_page()
        try:
            self.wait_until_status_present(name)
            return True
        except TimeoutException:
            return False

    def edit_status(
        self,
        current_name: str,
        new_name: str,
        new_slug: str | None = None,
    ) -> bool:
        self.open_page()
        self.safe_click(
            self.wait.until(
                EC.presence_of_element_located(
                    self._status_locator(current_name)
                )
            )
        )
        self.fill_input('input[name="name"]', new_name)

        if new_slug is not None:
            self.fill_input('input[name="slug"]', new_slug)

        self.click_icon("Save")
        self.open_page()
        try:
            self.wait_until_status_absent(current_name)
            self.wait_until_status_present(new_name)
            return True
        except TimeoutException:
            return False

    def delete_status(self, name: str) -> bool:
        self.open_page()
        self.safe_click(
            self.wait.until(
                EC.presence_of_element_located(self._status_locator(name))
            )
        )
        self.click_icon("Delete")
        self.open_page()
        try:
            self.wait_until_status_absent(name)
            return True
        except TimeoutException:
            return False

    def delete_all_statuses(self) -> bool:
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
