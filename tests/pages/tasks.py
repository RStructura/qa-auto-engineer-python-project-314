from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base import BasePage


class TasksPage(BasePage):
    route = "tasks"

    def __init__(self, driver, base_url: str):
        super().__init__(driver, base_url)
        self.filter_assignee_container = (
            By.CSS_SELECTOR,
            '[data-source="assignee_id"]',
        )
        self.filter_status_container = (
            By.CSS_SELECTOR,
            '[data-source="status_id"]',
        )
        self.filter_label_container = (
            By.CSS_SELECTOR,
            '[data-source="label_id"]',
        )

    def open_page(self) -> None:
        self.open(self.route)
        self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Create"]')
            )
        )

    def verify_filters_visible(self) -> bool:
        self.open_page()
        filters = {
            self.filter_assignee_container: "Assignee",
            self.filter_status_container: "Status",
            self.filter_label_container: "Label",
        }
        for locator, expected_text in filters.items():
            element = self.wait.until(
                EC.visibility_of_element_located(locator)
            )
            if expected_text not in element.text:
                return False
        return True

    def create_task(
        self,
        title: str,
        content: str,
        assignee_email: str,
        status_name: str,
    ) -> bool:
        self.open_page()
        self.click_icon("Create")
        self.select_from_dropdown(
            'input[name="assignee_id"]',
            assignee_email,
        )
        self.fill_input('input[name="title"]', title)
        if content:
            self.fill_input('textarea[name="content"]', content)
        self.select_from_dropdown('input[name="status_id"]', status_name)
        self.click_icon("Save")
        self.open_page()
        return self.task_exists(title)

    def task_exists(self, title: str) -> bool:
        self.open_page()
        try:
            self.wait_for_text(title)
        except TimeoutException:
            return False
        return True

    def _task_card_xpath(self, title: str) -> str:
        return (
            f"//*[normalize-space()='{title}']"
            "/ancestor::div[contains(@class,'MuiCard-root')]"
        )

    def _open_edit(self, title: str) -> None:
        card_xpath = self._task_card_xpath(title)
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, card_xpath))
        )
        edit_xpath = (
            f"{card_xpath}//button[@aria-label='Edit'] | "
            f"{card_xpath}//a[@aria-label='Edit']"
        )
        edit_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, edit_xpath))
        )
        self.safe_click(edit_button)

    def edit_task(
        self,
        title: str,
        *,
        new_title: str | None = None,
        new_content: str | None = None,
        new_status: str | None = None,
    ) -> bool:
        self.open_page()
        self._open_edit(title)

        if new_title is not None:
            self.fill_input('input[name="title"]', new_title)

        if new_content is not None:
            self.fill_input('textarea[name="content"]', new_content)

        if new_status is not None:
            self.select_from_dropdown(
                'input[name="status_id"]',
                new_status,
            )

        self.click_icon("Save")
        updated_title = new_title or title
        self.open_page()
        return self.task_exists(updated_title)

    def open_task_details(self, title: str) -> None:
        self.open_page()
        card_xpath = self._task_card_xpath(title)
        show_xpath = (
            f"{card_xpath}//button[@aria-label='Show'] | "
            f"{card_xpath}//a[@aria-label='Show']"
        )
        show_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, show_xpath))
        )
        self.safe_click(show_button)

    def is_task_in_status(self, title: str, status_name: str) -> bool:
        self.open_page()
        column_xpath = (
            f"//*[normalize-space()='{status_name}']"
            "/following::div[@data-rfd-droppable-id][1]"
        )
        try:
            column = self.wait.until(
                EC.presence_of_element_located((By.XPATH, column_xpath))
            )
            column.find_element(
                By.XPATH,
                ".//div[contains(@class,'MuiCard-root')]"
                f"//*[normalize-space()='{title}']",
            )
        except TimeoutException:
            return False
        except NoSuchElementException:
            return False
        return True
