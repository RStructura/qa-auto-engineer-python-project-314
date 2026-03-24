import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TasksPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

        # Локаторы_old
        # self.tasks_url = (By.CSS_SELECTOR, 'a[href="#/tasks"]')
        # self.create_btn = (By.CSS_SELECTOR, 'a[href="#/tasks/create"]')
        # self.task_elements = (By.CSS_SELECTOR, '[data-rfd-draggable-id]')
        # self.name_input = (By.NAME, "title")
        # self.description_input = (By.NAME, "content")
        # self.save_btn = (By.CSS_SELECTOR, 'button[type="submit"]')
        # self.delete_btn = (By.CSS_SELECTOR, '[aria-label="Delete"]')

        # Локаторы_new
        self.url_tasks = (By.CSS_SELECTOR, 'a[href="#/tasks"]')
        self.element_task = (By.CSS_SELECTOR, '[data-rfd-draggable-id]')
        self.input_name = (By.NAME, "title")
        self.input_description = (By.NAME, "content")
        self.btn_create = (By.CSS_SELECTOR, '[aria-label="Create"]')
        self.btn_save = (By.CSS_SELECTOR, '[aria-label="Save"]')
        self.btn_edit = (By.CSS_SELECTOR, '[aria-label="Edit"]')
        self.btn_show = (By.CSS_SELECTOR, '[aria-label="Show"]')
        self.btn_delete = (By.CSS_SELECTOR, '[aria-label="Delete"]')


# НАВИГАЦИЯ НА СТРАНИЦУ
    def open_tasks(self):
        self.wait.until(EC.element_to_be_clickable(self.url_tasks)).click()


# ПОЛУЧЕНИЕ ДАННЫХ ДЛЯ ПРОВЕРОК
    # Получение контекста для проверок изменения канбана
    def get_page_context(self):
        return self.driver.find_element(By.TAG_NAME, "body").text

    def get_all_task_ids(self):
        # Поиск задач по локатору
        found_elements = self.driver.find_elements(*self.element_task)
        ids = []
        for el in found_elements:
            task_id = el.get_attribute('data-rfd-draggable-id')
            if task_id and task_id.isdigit():
                ids.append(int(task_id))
        return ids

    # Подсчет задач
    def get_tasks_count(self):
        return len(self.get_all_task_ids())

    # Проверка изменения количества задач
    def get_next_task_number(self):
        ids = self.get_all_task_ids()
        return max(ids) + 1 if ids else 1


# РАБОТА С ФИЛЬТРАМИ
    # Выпадание фильтра и выбор значения
    def select_filter(self, input_name, value):
        # Поиск скрытого input
        input_element = self.wait.until(
            EC.presence_of_element_located((By.NAME, input_name)))

        # Поиск combobox фильтра
        combobox = input_element.find_element(
            By.XPATH,
            "../div[@role='combobox']")

        # Клик в фильтр
        self.wait.until(EC.element_to_be_clickable(combobox))
        combobox.click()

        # Ожидание выпадания списка
        option = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//li[contains(., '{value}')]")))

        # Клик в значение списка
        option.click()

        # Ожидание закрытия списка
        time.sleep(0.5)

    # Фильтры
    def filter_by_assignee(self, assignee):
        self.select_filter("assignee_id", assignee)

    def filter_by_status(self, status):
        self.select_filter("status_id", status)

    def filter_by_label(self, label):
        self.select_filter("label_id", label)


# СОЗДАНИЕ ЗАДАЧ
    def select_option(self, input_name, text):
        input_element = self.wait.until(
            EC.presence_of_element_located((By.NAME, input_name)))
        combobox = input_element.find_element(By.XPATH, "../div[@role='combobox']")

        # Скролл к элементу и клик
        self.driver.execute_script(
            "arguments[0].scrollIntoView(true);", combobox)
        combobox.click()
        
        # Выбор значения по тексту
        option = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//li[contains(., '{text}')]")))
        option.click()

        # Закрытие списка по нажатию по Escape
        self.driver.switch_to.active_element.send_keys(Keys.ESCAPE)

    def create_task(self, assignee, title, content, status, labels):
        self.wait.until(EC.element_to_be_clickable(self.btn_create)).click()
        # Assignee
        self.select_option("assignee_id", assignee)
        # Title
        self.wait.until(EC.visibility_of_element_located(self.input_name)
        ).send_keys(title)
        # Content
        self.driver.find_element(*self.input_description).send_keys(content)
        # Status
        self.select_option("status_id", status)
        # Labels
        for label in labels:
            self.select_option("label_id", label)
        # Save
        self.wait.until(EC.element_to_be_clickable(self.btn_save)).click()


# РЕДАКТИРОВАНИЕ ЗАДАЧ
    def open_task_edit(self, task_id):
        # Связь ID задачи и кнопки Edit через вложенность
        edit_locator = (By.CSS_SELECTOR, f'[data-rfd-draggable-id="{task_id}"] a[aria-label="Edit"]')
        self.wait.until(EC.element_to_be_clickable(edit_locator)).click()

    def clear_text_field(self, locator):
        element = self.wait.until(EC.visibility_of_element_located(locator)).click()        
        actions = ActionChains(self.driver)
        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        actions.send_keys(Keys.BACKSPACE).perform()

    def clear_labels(self, current_labels):
        for label in current_labels:
            self.select_option("label_id", label)

    def update_task_fields(self, title=None, content=None, assignee=None, status=None, new_labels=None, old_labels=None):
        if assignee:
            self.select_option("assignee_id", assignee)
        if title:
            self.clear_text_field(self.input_name)
            self.driver.find_element(*self.input_name).send_keys(title)
        if content:
            self.clear_text_field(self.input_description)
            self.driver.find_element(*self.input_description).send_keys(content)
        if status:
            self.select_option("status_id", status)
        if old_labels:
            self.clear_labels(old_labels)
        if new_labels:
            for label in new_labels:
                self.select_option("label_id", label)
        self.wait.until(EC.element_to_be_clickable(self.btn_save)).click()


# ПЕРЕМЕЩЕНИЕ ЗАДАЧ
    def move_task_to_status(self, task_id, target_status):
        # Поиск задач
        handle_xpath = f'//div[@data-rfd-drag-handle-draggable-id="{task_id}"]'
        handle = self.wait.until(EC.presence_of_element_located((By.XPATH, handle_xpath)))

        # Поиск активной зоны дропа
        column_xpath = f"//h6[text()='{target_status}']/following-sibling::div[@data-rfd-droppable-id]"
        target_column = self.wait.until(EC.presence_of_element_located((By.XPATH, column_xpath)))

        actions = ActionChains(self.driver)
        
        # Алгоритм действий для перемещния
        (actions
         .move_to_element(handle)
         .click_and_hold(handle)
         .move_by_offset(5, 5)
         .pause(0.5)
         .move_to_element(target_column)
         .pause(0.5)
         .release()
         .perform())
        
        # Ожидание завершения анимации перемещения в интерфейсе
        time.sleep(0.5)

    def is_task_in_column(self, task_id, status_name):
        """Проверяет наличие карточки в конкретной колонке."""
        xpath = (f"//h6[text()='{status_name}']/following-sibling::div"
                 f"//div[@data-rfd-draggable-id='{task_id}']")
        try:
            return self.driver.find_element(By.XPATH, xpath).is_displayed()
        except:
            return False


# УДАЛЕНИЕ ЗАДАЧ
    def open_task_delete (self, task_id):
        # Связь ID задачи и кнопки Edit через вложенность
        show_locator = (By.CSS_SELECTOR, f'[data-rfd-draggable-id="{task_id}"] a[aria-label="Show"]')
        self.wait.until(EC.element_to_be_clickable(show_locator)).click()

    def delete_task(self):
        self.wait.until(EC.element_to_be_clickable(self.btn_delete)).click()