from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class LabelsPage:
    def __init__(self, driver):
        self.driver = driver


# НАВИГАЦИЯ НА СТРАНИЦУ
    def open_labels(self):
        self.driver.find_element(By.CSS_SELECTOR, 'a[href="#/labels"]').click()


# ПОЛУЧЕНИЕ ДАННЫХ ДЛЯ ПРОВЕРОК
    def get_labels_count(self):
        return len(self.driver.find_elements(
            By.CSS_SELECTOR, 'tr.RaDatagrid-row'))

    def get_first_label_name(self):
        return self.driver.find_element(By.CSS_SELECTOR, 'td.column-name').text

    def get_error_message(self):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, "p.Mui-error").text
        except NoSuchElementException:
            return ""

    def is_label_present(self, name):
        elements = self.driver.find_elements(
            By.XPATH,
            f"//td[contains(@class, 'column-name')"
            f" and normalize-space()='{name}']"
        )
        return len(elements) > 0


# РАБОТА СО СПИСКОМ
    def open_first_label(self):
        self.driver.find_element(
            By.CSS_SELECTOR, 'tbody tr:first-child').click()

    def select_first_checkbox(self):
        self.driver.find_element(
            By.CSS_SELECTOR, 'tbody input[type="checkbox"]').click()

    def select_all_checkbox(self):
        self.driver.find_element(
            By.CSS_SELECTOR, 'thead input[type="checkbox"]').click()

    def click_delete_button(self):
        self.driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label="Delete"]').click()

    def is_empty_message_visible(self):
        try:
            return self.driver.find_element(
                By.CSS_SELECTOR, '.RaEmpty-message').is_displayed()
        except NoSuchElementException:
            return False


# СОЗДАНИЕ/РЕДАКТИРОВАНИЕ ЛЕЙБЛА
    def click_create(self):
        self.driver.find_element(
            By.CSS_SELECTOR, 'a[href="#/labels/create"]').click()

    def fill_label_form(self, name=None):
        if name:
            self.driver.find_element(By.NAME, "name").send_keys(name)

    def click_save(self):
        self.driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]').click()

    def force_clear_input(self, field_name):
        element = self.driver.find_element(By.NAME, field_name)
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click().click().click().perform()
        element.send_keys(Keys.BACKSPACE)


