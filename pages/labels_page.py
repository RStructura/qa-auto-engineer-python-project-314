from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LabelsPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # -----------------------------------------------------------------
    # НАВИГАЦИЯ
    # -----------------------------------------------------------------

    def open_labels(self):
        """Открыть страницу labels и дождаться списка или empty state."""
        self.driver.find_element(By.CSS_SELECTOR, 'a[href="#/labels"]').click()

        self.wait.until(
            lambda d: (
                len(d.find_elements(By.CSS_SELECTOR, "table")) > 0
                or len(d.find_elements(By.CSS_SELECTOR, ".RaEmpty-message")) > 0
            )
        )

    # -----------------------------------------------------------------
    # ПОЛУЧЕНИЕ ДАННЫХ ДЛЯ ПРОВЕРОК
    # -----------------------------------------------------------------

    def get_labels_count(self):
        return len(
            self.driver.find_elements(By.CSS_SELECTOR, "tr.RaDatagrid-row")
        )

    def get_all_label_names(self):
        elements = self.driver.find_elements(
            By.CSS_SELECTOR,
            "tbody td.column-name",
        )
        return [
            element.text.strip()
            for element in elements
            if element.text.strip()
        ]

    def get_first_label_name(self):
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

    def get_label_row(self, name):
        return self.driver.find_element(
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-name') "
            f"and normalize-space()='{name}']]",
        )

    def get_label_row_values(self, name):
        row = self.get_label_row(name)
        return {
            "name": row.find_element(
                By.CSS_SELECTOR,
                "td.column-name",
            ).text.strip(),
        }

    def is_label_present(self, name):
        elements = self.driver.find_elements(
            By.XPATH,
            f"//td[contains(@class, 'column-name') "
            f"and normalize-space()='{name}']",
        )
        return len(elements) > 0

    def wait_for_label_present(self, name):
        self.wait.until(
            lambda d: len(
                d.find_elements(
                    By.XPATH,
                    f"//td[contains(@class, 'column-name') "
                    f"and normalize-space()='{name}']",
                )
            ) > 0
        )

    def wait_for_label_absent(self, name):
        self.wait.until(
            lambda d: len(
                d.find_elements(
                    By.XPATH,
                    f"//td[contains(@class, 'column-name') "
                    f"and normalize-space()='{name}']",
                )
            ) == 0
        )

    def wait_for_empty_state(self):
        """Ожидание empty state после удаления всех labels"""
        self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".RaEmpty-message")
            )
        )

    # -----------------------------------------------------------------
    # РАБОТА СО СПИСКОМ
    # -----------------------------------------------------------------

    def open_label_by_name(self, name):
        self.get_label_row(name).click()

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
            'a[href="#/labels/create"]',
        ).click()

        self.wait.until(
            EC.visibility_of_element_located((By.NAME, "name"))
        )

    def fill_label_form(self, name=None):
        if name:
            self.driver.find_element(By.NAME, "name").send_keys(name)

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