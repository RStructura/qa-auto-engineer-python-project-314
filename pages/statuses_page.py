from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class StatusesPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # -----------------------------------------------------------------
    # НАВИГАЦИЯ
    # -----------------------------------------------------------------

    def open_statuses(self):
        """Открыть страницу statuses и дождаться списка или empty state."""
        self.driver.find_element(
            By.CSS_SELECTOR,
            'a[href="#/task_statuses"]',
        ).click()

        self.wait.until(
            lambda d: (
                len(d.find_elements(By.CSS_SELECTOR, "table")) > 0
                or len(d.find_elements(By.CSS_SELECTOR, ".RaEmpty-message")) > 0
            )
        )

    # -----------------------------------------------------------------
    # ПОЛУЧЕНИЕ ДАННЫХ ДЛЯ ПРОВЕРОК
    # -----------------------------------------------------------------

    def get_statuses_count(self):
        return len(
            self.driver.find_elements(By.CSS_SELECTOR, "tr.RaDatagrid-row")
        )

    def get_all_status_names(self):
        elements = self.driver.find_elements(
            By.CSS_SELECTOR,
            "tbody td.column-name",
        )
        return [
            element.text.strip()
            for element in elements
            if element.text.strip()
        ]

    def get_first_status_name(self):
        return self.driver.find_element(
            By.CSS_SELECTOR,
            "td.column-name",
        ).text.strip()

    def get_error_message(self):
        try:
            return self.driver.find_element(
                By.CSS_SELECTOR,
                "p.Mui-error",
            ).text
        except NoSuchElementException:
            return ""

    def get_status_row_text(self, name):
        row = self.driver.find_element(
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-name') "
            f"and normalize-space()='{name}']]",
        )
        return row.text

    def is_status_present(self, name):
        elements = self.driver.find_elements(
            By.XPATH,
            f"//td[contains(@class, 'column-name') "
            f"and normalize-space()='{name}']",
        )
        return len(elements) > 0

    def wait_for_status_present(self, name):
        self.wait.until(
            lambda d: len(
                d.find_elements(
                    By.XPATH,
                    f"//td[contains(@class, 'column-name') "
                    f"and normalize-space()='{name}']",
                )
            ) > 0
        )

    def wait_for_status_absent(self, name):
        self.wait.until(
            lambda d: len(
                d.find_elements(
                    By.XPATH,
                    f"//td[contains(@class, 'column-name') "
                    f"and normalize-space()='{name}']",
                )
            ) == 0
        )

    # -----------------------------------------------------------------
    # РАБОТА СО СПИСКОМ
    # -----------------------------------------------------------------

    def open_first_status(self):
        self.driver.find_element(
            By.CSS_SELECTOR,
            "tbody tr:first-child",
        ).click()

    def open_status_by_name(self, name):
        self.driver.find_element(
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-name') "
            f"and normalize-space()='{name}']]",
        ).click()

    def select_first_checkbox(self):
        self.driver.find_element(
            By.CSS_SELECTOR,
            "tbody input[type='checkbox']",
        ).click()

    def select_checkbox_by_name(self, name):
        checkbox = self.driver.find_element(
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-name') "
            f"and normalize-space()='{name}']]//input[@type='checkbox']",
        )
        checkbox.click()

    def select_all_checkbox(self):
        self.driver.find_element(
            By.CSS_SELECTOR,
            "thead input[type='checkbox']",
        ).click()

    def click_delete_button(self):
        self.driver.find_element(
            By.CSS_SELECTOR,
            'button[aria-label="Delete"]',
        ).click()

    def is_empty_message_visible(self):
        try:
            return self.driver.find_element(
                By.CSS_SELECTOR,
                ".RaEmpty-message",
            ).is_displayed()
        except NoSuchElementException:
            return False

    # -----------------------------------------------------------------
    # СОЗДАНИЕ / РЕДАКТИРОВАНИЕ
    # -----------------------------------------------------------------

    def click_create(self):
        self.driver.find_element(
            By.CSS_SELECTOR,
            'a[href="#/task_statuses/create"]',
        ).click()

        self.wait.until(
            EC.visibility_of_element_located((By.NAME, "name"))
        )

    def fill_status_form(self, name=None, slug=None):
        if name:
            self.driver.find_element(By.NAME, "name").send_keys(name)
        if slug:
            self.driver.find_element(By.NAME, "slug").send_keys(slug)

    def click_save(self):
        self.driver.find_element(
            By.CSS_SELECTOR,
            'button[type="submit"]',
        ).click()

    def force_clear_input(self, field_name):
        element = self.driver.find_element(By.NAME, field_name)
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click().click().click().perform()
        element.send_keys(Keys.BACKSPACE)