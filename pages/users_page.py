from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class UsersPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # -----------------------------------------------------------------
    # НАВИГАЦИЯ
    # -----------------------------------------------------------------

    def open_users(self):
        """Открыть страницу users и дождаться списка или empty state."""
        self.driver.find_element(By.CSS_SELECTOR, 'a[href="#/users"]').click()

        self.wait.until(
            lambda d: (
                len(d.find_elements(By.CSS_SELECTOR, "table")) > 0
                or len(d.find_elements(By.CSS_SELECTOR, ".RaEmpty-message")) > 0
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
        return [element.text.strip()
            for element in elements
                if element.text.strip()
        ]

    def get_first_user_email(self):
        return self.driver.find_element(
            By.CSS_SELECTOR,
            "td.column-email",
        ).text.strip()

    def get_error_message(self):
        try:
            return self.driver.find_element(
                By.CSS_SELECTOR,
                "p.Mui-error",
            ).text
        except NoSuchElementException:
            return ""

    def get_user_row_text(self, email):
        row = self.driver.find_element(
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-email') "
            f"and normalize-space()='{email}']]",
        )
        return row.text

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

    # -----------------------------------------------------------------
    # РАБОТА СО СПИСКОМ
    # -----------------------------------------------------------------

    def open_first_user(self):
        self.driver.find_element(
            By.CSS_SELECTOR,
            "tbody tr:first-child",
        ).click()

    def open_user_by_email(self, email):
        self.driver.find_element(
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-email') "
            f"and normalize-space()='{email}']]",
        ).click()

    def select_first_checkbox(self):
        self.driver.find_element(
            By.CSS_SELECTOR,
            "tbody input[type='checkbox']",
        ).click()

    def select_checkbox_by_email(self, email):
        checkbox = self.driver.find_element(
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-email') "
            f"and normalize-space()='{email}']]//input[@type='checkbox']",
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
            'a[href="#/users/create"]',
        ).click()

        self.wait.until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )

    def fill_user_form(self, email=None, first=None, last=None):
        if email:
            self.driver.find_element(By.NAME, "email").send_keys(email)
        if first:
            self.driver.find_element(By.NAME, "firstName").send_keys(first)
        if last:
            self.driver.find_element(By.NAME, "lastName").send_keys(last)

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