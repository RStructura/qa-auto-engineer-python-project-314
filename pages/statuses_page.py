from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class StatusesPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        self.nav_link = (By.CSS_SELECTOR, 'a[href="#/task_statuses"]')
        self.delete_button = (By.CSS_SELECTOR, 'button[aria-label="Delete"]')
        self.name_input = (By.NAME, "name")
        self.slug_input = (By.NAME, "slug")

    # -----------------------------------------------------------------
    # НАВИГАЦИЯ
    # -----------------------------------------------------------------

    def open_statuses(self):
        self.wait.until(
            EC.element_to_be_clickable(self.nav_link)
        ).click()

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

    def get_error_message(self):
        try:
            return self.driver.find_element(
                By.CSS_SELECTOR,
                "p.Mui-error",
            ).text
        except NoSuchElementException:
            return ""

    def get_input_value(self, field_name):
        return self.driver.find_element(
            By.NAME,
            field_name,
        ).get_attribute("value")

    def get_status_row(self, name):
        return self.driver.find_element(
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-name') "
            f"and normalize-space()='{name}']]",
        )

    def get_status_row_values(self, name):
        row = self.get_status_row(name)
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

    def wait_for_empty_state(self):
        self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".RaEmpty-message")
            )
        )

    # -----------------------------------------------------------------
    # ВСПОМОГАТЕЛЬНЫЕ КЛИКИ
    # -----------------------------------------------------------------

    def _click_checkbox(self, locator):
        checkbox = self.wait.until(
            EC.presence_of_element_located(locator)
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            checkbox,
        )

        try:
            checkbox.click()
        except (
            ElementClickInterceptedException,
            StaleElementReferenceException,
            WebDriverException,
        ):
            self.driver.execute_script(
                "arguments[0].click();",
                checkbox,
            )

    def _click_button(self, locator):
        button = self.wait.until(
            EC.presence_of_element_located(locator)
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            button,
        )

        self.wait.until(lambda d: d.find_element(*locator).is_enabled())

        try:
            button.click()
        except (
            ElementClickInterceptedException,
            StaleElementReferenceException,
            WebDriverException,
        ):
            self.driver.execute_script(
                "arguments[0].click();",
                button,
            )

    # -----------------------------------------------------------------
    # РАБОТА СО СПИСКОМ
    # -----------------------------------------------------------------

    def open_status_by_name(self, name):
        self.get_status_row(name).click()

    def select_checkbox_by_name(self, name):
        locator = (
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-name') "
            f"and normalize-space()='{name}']]//input[@type='checkbox']",
        )
        self._click_checkbox(locator)

    def select_all_checkbox(self):
        locator = (
            By.CSS_SELECTOR,
            "thead input[type='checkbox']",
        )
        self._click_checkbox(locator)

    def click_delete_button(self):
        self._click_button(self.delete_button)

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
        self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a[href="#/task_statuses/create"]')
            )
        ).click()

        self.wait.until(
            EC.visibility_of_element_located(self.name_input)
        )

    def fill_status_form(self, name=None, slug=None):
        if name is not None:
            self.driver.find_element(*self.name_input).send_keys(name)
        if slug is not None:
            self.driver.find_element(*self.slug_input).send_keys(slug)

    def click_save(self):
        self._click_button((By.CSS_SELECTOR, 'button[type="submit"]'))

    def force_clear_input(self, field_name):
        element = self.wait.until(
            EC.visibility_of_element_located((By.NAME, field_name))
        )
        element.click()

        actions = ActionChains(self.driver)
        (
            actions
            .key_down(Keys.CONTROL)
            .send_keys("a")
            .key_up(Keys.CONTROL)
            .send_keys(Keys.BACKSPACE)
            .perform()
        )

        self.driver.execute_script(
            (
                "arguments[0].dispatchEvent("
                "new Event('input', {bubbles: true})"
                ");"
                "arguments[0].dispatchEvent("
                "new Event('change', {bubbles: true})"
                ");"
            ),
            element,
        )

        self.wait.until(
            lambda d: d.find_element(
                By.NAME,
                field_name,
            ).get_attribute("value") == ""
        )
