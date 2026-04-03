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


class UsersPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        self.nav_link = (By.CSS_SELECTOR, 'a[href="#/users"]')
        self.delete_button = (By.CSS_SELECTOR, 'button[aria-label="Delete"]')
        self.email_input = (By.NAME, "email")
        self.first_input = (By.NAME, "firstName")
        self.last_input = (By.NAME, "lastName")

    # -----------------------------------------------------------------
    # НАВИГАЦИЯ
    # -----------------------------------------------------------------

    def open_users(self):
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

    def get_users_count(self):
        return len(
            self.driver.find_elements(By.CSS_SELECTOR, "tr.RaDatagrid-row")
        )

    def get_all_user_emails(self):
        elements = self.driver.find_elements(
            By.CSS_SELECTOR,
            "tbody td.column-email",
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

    def get_user_row(self, email):
        return self.driver.find_element(
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-email') "
            f"and normalize-space()='{email}']]",
        )

    def get_user_row_values(self, email):
        row = self.get_user_row(email)
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

    def is_user_present(self, email):
        elements = self.driver.find_elements(
            By.XPATH,
            f"//td[contains(@class, 'column-email') "
            f"and normalize-space()='{email}']",
        )
        return len(elements) > 0

    def wait_for_user_present(self, email):
        self.wait.until(
            lambda d: len(
                d.find_elements(
                    By.XPATH,
                    f"//td[contains(@class, 'column-email') "
                    f"and normalize-space()='{email}']",
                )
            ) > 0
        )

    def wait_for_user_absent(self, email):
        self.wait.until(
            lambda d: len(
                d.find_elements(
                    By.XPATH,
                    f"//td[contains(@class, 'column-email') "
                    f"and normalize-space()='{email}']",
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

    def open_user_by_email(self, email):
        self.get_user_row(email).click()

    def select_checkbox_by_email(self, email):
        locator = (
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-email') "
            f"and normalize-space()='{email}']]//input[@type='checkbox']",
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
                (By.CSS_SELECTOR, 'a[href="#/users/create"]')
            )
        ).click()

        self.wait.until(
            EC.visibility_of_element_located(self.email_input)
        )

    def fill_user_form(self, email=None, first=None, last=None):
        if email is not None:
            self.driver.find_element(*self.email_input).send_keys(email)
        if first is not None:
            self.driver.find_element(*self.first_input).send_keys(first)
        if last is not None:
            self.driver.find_element(*self.last_input).send_keys(last)

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
