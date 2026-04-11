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


class LabelsPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        self.nav_link = (By.CSS_SELECTOR, 'a[href="#/labels"]')
        self.delete_button = (
            By.CSS_SELECTOR,
            'button[aria-label="Delete"]',
        )
        self.name_input = (By.NAME, "name")

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

    def open_labels(self):
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

    def get_labels_count(self):
        return len(
            self.driver.find_elements(
                By.CSS_SELECTOR,
                "tbody tr.RaDatagrid-row",
            )
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
        self.open_labels()
        return self.wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "table"))
        )

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
        self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".RaEmpty-message")
            )
        )

    def open_label_by_name(self, name):
        self._safe_click(self.get_label_row(name))

    def select_checkbox_by_name(self, name):
        checkbox = self.driver.find_element(
            By.XPATH,
            "//tr[.//td[contains(@class, 'column-name') "
            f"and normalize-space()='{name}']]"
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
                (By.CSS_SELECTOR, 'a[href="#/labels/create"]')
            )
        ).click()
        self.wait.until(
            EC.visibility_of_element_located(self.name_input)
        )

    def fill_label_form(self, name=None):
        if name is not None:
            self.driver.find_element(
                *self.name_input
            ).send_keys(name)

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

    def create_label(self, name):
        self.open_labels()
        self.click_create()
        self.fill_label_form(name=name)
        self.click_save()
        self.open_labels()
        self.wait_for_label_present(name)
        return self.is_label_present(name)

    def edit_label(self, current_name, new_name):
        self.open_labels()
        self.open_label_by_name(current_name)
        self.force_clear_input("name")
        self.fill_label_form(name=new_name)
        self.click_save()
        self.open_labels()
        self.wait_for_label_present(new_name)
        return (
            self.is_label_present(new_name)
            and not self.is_label_present(current_name)
        )

    def delete_label(self, name):
        self.open_labels()
        self.open_label_by_name(name)
        self.click_delete_button()
        self.open_labels()
        self.wait_for_label_absent(name)
        return not self.is_label_present(name)

    def delete_all_labels(self):
        self.open_labels()
        if self.get_labels_count() == 0:
            return True
        self.select_all_checkbox()
        self.click_delete_button()
        self.open_labels()
        self.wait_for_empty_state()
        return self.get_labels_count() == 0
