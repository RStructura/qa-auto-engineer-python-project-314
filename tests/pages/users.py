from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base import BasePage


class UsersPage(BasePage):
    route = "users"

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

    def _user_locator(self, email: str):
        return (
            By.XPATH,
            "//td[contains(@class, 'column-email') "
            f"and normalize-space()='{email}']",
        )

    def wait_until_user_present(self, email: str) -> None:
        self.wait.until(
            lambda d: len(d.find_elements(*self._user_locator(email))) > 0
        )

    def wait_until_user_absent(self, email: str) -> None:
        self.wait.until(
            lambda d: len(d.find_elements(*self._user_locator(email))) == 0
        )

    def get_table(self):
        self.open_page()
        return self.wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "table"))
        )

    def get_user_row_values(self, email: str) -> dict[str, str]:
        self.open_page()
        row = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//tr[.//td[contains(@class, 'column-email') "
                    f"and normalize-space()='{email}']]",
                )
            )
        )
        return {
            "email": row.find_element(
                By.CSS_SELECTOR,
                "td.column-email",
            ).text.strip(),
            "first": row.find_element(
                By.CSS_SELECTOR,
                "td.column-firstName",
            ).text.strip(),
            "last": row.find_element(
                By.CSS_SELECTOR,
                "td.column-lastName",
            ).text.strip(),
        }

    def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
    ) -> bool:
        self.open_page()
        self.click_icon("Create")
        self.fill_input('input[name="email"]', email)
        self.fill_input('input[name="firstName"]', first_name)
        self.fill_input('input[name="lastName"]', last_name)
        self.click_icon("Save")
        self.open_page()
        try:
            self.wait_until_user_present(email)
            return True
        except TimeoutException:
            return False

    def edit_user(self, email: str, new_first_name: str) -> bool:
        self.open_page()
        self.safe_click(
            self.wait.until(
                EC.presence_of_element_located(self._user_locator(email))
            )
        )
        self.fill_input('input[name="firstName"]', new_first_name)
        self.click_icon("Save")
        self.open_page()
        try:
            self.wait_for_text(new_first_name)
            return True
        except TimeoutException:
            return False

    def delete_user(self, email: str) -> bool:
        self.open_page()
        self.safe_click(
            self.wait.until(
                EC.presence_of_element_located(self._user_locator(email))
            )
        )
        self.click_icon("Delete")
        self.open_page()
        try:
            self.wait_until_user_absent(email)
            return True
        except TimeoutException:
            return False

    def delete_all_users(self) -> bool:
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
