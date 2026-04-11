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
        self.delete_button = (
            By.CSS_SELECTOR,
            'button[aria-label="Delete"]',
        )
        self.email_input = (By.NAME, "email")
        self.first_input = (By.NAME, "firstName")
        self.last_input = (By.NAME, "lastName")

    def _safe_click(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element,
        )
        try:
            element.click()
        except (
            ElementClickInterceptedException,
            StaleElementReferenceException,
            WebDriverException,
        ):
            self.driver.execute_script("arguments[0].click();", element)

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

    def get_users_count(self):
        return len(
            self.driver.find_elements(
                By.CSS_SELECTOR,
                "tbody tr.RaDatagrid-row",
            )
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

    def get_table(self):
        self.open_users()
        return self.wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "table"))
        )

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

    def open_user_by_email(self, email):
        self._safe_click(self.get_user_row(email))

    def select_checkbox_by_email(self, email):
        checkbox = self.driver.find_element(
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-email') "
            f"and normalize-space()='{email}']]"
            "//input[@type='checkbox']",
        )
        self._safe_click(checkbox)

    def select_all_checkbox(self):
        checkbox = self.driver.find_element(
            By.CSS_SELECTOR,
            "thead input[type='checkbox']",
        )
        self._safe_click(checkbox)

    def click_delete_button(self):
        button = self.wait.until(
            EC.presence_of_element_located(self.delete_button)
        )
        self._safe_click(button)

    def is_empty_message_visible(self):
        try:
            return self.driver.find_element(
                By.CSS_SELECTOR,
                ".RaEmpty-message",
            ).is_displayed()
        except NoSuchElementException:
            return False

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
            self.driver.find_element(
                *self.email_input
            ).send_keys(email)
        if first is not None:
            self.driver.find_element(
                *self.first_input
            ).send_keys(first)
        if last is not None:
            self.driver.find_element(
                *self.last_input
            ).send_keys(last)

    def click_save(self):
        button = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[type="submit"]')
            )
        )
        self._safe_click(button)

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

    def create_user(self, email, first_name, last_name):
        self.open_users()
        self.click_create()
        self.fill_user_form(
            email=email,
            first=first_name,
            last=last_name,
        )
        self.click_save()
        self.open_users()
        self.wait_for_user_present(email)
        return self.is_user_present(email)

    def edit_user(
        self,
        email,
        new_first_name,
        new_last_name=None,
        new_email=None,
    ):
        self.open_users()
        self.open_user_by_email(email)
        self.force_clear_input("firstName")
        self.fill_user_form(first=new_first_name)
        if new_last_name is not None:
            self.force_clear_input("lastName")
            self.fill_user_form(last=new_last_name)
        if new_email is not None:
            self.force_clear_input("email")
            self.fill_user_form(email=new_email)
        self.click_save()
        result_email = new_email or email
        self.open_users()
        self.wait_for_user_present(result_email)
        return (
            self.is_user_present(result_email)
            and (new_email is None or not self.is_user_present(email))
        )

    def delete_user(self, email):
        self.open_users()
        self.open_user_by_email(email)
        self.click_delete_button()
        self.open_users()
        self.wait_for_user_absent(email)
        return not self.is_user_present(email)

    def delete_all_users(self):
        self.open_users()
        if self.get_users_count() == 0:
            return True
        self.select_all_checkbox()
        self.click_delete_button()
        self.open_users()
        self.wait_for_empty_state()
        return self.get_users_count() == 0
