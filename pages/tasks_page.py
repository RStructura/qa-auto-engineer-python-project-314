import time

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TasksPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

        # Основные локаторы страницы tasks
        self.url_tasks = (By.CSS_SELECTOR, 'a[href="#/tasks"]')
        self.element_task = (By.CSS_SELECTOR, '[data-rfd-draggable-id]')

        # Контейнеры фильтров
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

        # Поля формы
        self.input_name = (By.NAME, "title")
        self.input_description = (By.NAME, "content")

        # Кнопки
        self.btn_create = (By.CSS_SELECTOR, '[aria-label="Create"]')
        self.btn_save = (By.CSS_SELECTOR, '[aria-label="Save"]')
        self.btn_delete = (By.CSS_SELECTOR, '[aria-label="Delete"]')

    # -----------------------------------------------------------------
    # НАВИГАЦИЯ
    # -----------------------------------------------------------------

    def open_tasks(self):
        """Открытие страницы канбан-доски tasks"""
        self.wait.until(EC.element_to_be_clickable(self.url_tasks)).click()
        # Ожидание фильтра ассайни для подтверждения загрузки доски
        self.wait.until(
            EC.visibility_of_element_located(
                self.filter_assignee_container
            )
        )

    def open_task_edit(self, task_id):
        """Открытие формы редактирования задачи по id"""
        edit_locator = (
            By.CSS_SELECTOR,
            f'[data-rfd-draggable-id="{task_id}"] a[aria-label="Edit"]',
        )
        self.wait.until(EC.element_to_be_clickable(edit_locator)).click()

    def open_task_show(self, task_id):
        """Открытие show-страницы задачи по id"""
        show_locator = (
            By.CSS_SELECTOR,
            f'[data-rfd-draggable-id="{task_id}"] a[aria-label="Show"]',
        )
        self.wait.until(EC.element_to_be_clickable(show_locator)).click()

    def open_task_delete(self, task_id):
        """Метод для удаления задачи через show-страницу"""
        self.open_task_show(task_id)

    # -----------------------------------------------------------------
    # ДАННЫЕ ДЛЯ ПРОВЕРОК
    # -----------------------------------------------------------------

    def get_page_context(self):
        """Получение текста всей страницы как есть"""
        return self.driver.find_element(By.TAG_NAME, "body").text

    def get_current_page_text(self):
        """Получение текста текущей страницы в нижнем регистре."""
        return self.wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "body"))
        ).text.lower()

    def get_all_task_ids(self):
        """Сбор все id задач, которые сейчас видны на доске"""
        found_elements = self.driver.find_elements(*self.element_task)
        ids = []

        for element in found_elements:
            task_id = element.get_attribute("data-rfd-draggable-id")
            if task_id and task_id.isdigit():
                ids.append(int(task_id))

        return ids

    def get_tasks_count(self):
        """Количество видимых задач на доске"""
        return len(self.get_all_task_ids())

    def _extract_card_lines(self, text):
        """Нормализация строк задачи"""
        return [line.strip() for line in text.splitlines() if line.strip()]

    def find_task_id_by_title(self, title):
        """Поиск id задачи по title на доске"""
        cards = self.driver.find_elements(*self.element_task)

        for card in cards:
            lines = self._extract_card_lines(card.text)
            if lines and lines[0] == title:
                task_id = card.get_attribute("data-rfd-draggable-id")
                if task_id and task_id.isdigit():
                    return int(task_id)

        return None

    def is_task_present(self, task_id):
        """Проверка видимости задачи на доске"""
        elements = self.driver.find_elements(
            By.CSS_SELECTOR,
            f'[data-rfd-draggable-id="{task_id}"]',
        )
        return len(elements) > 0

    def get_task_title(self, task_id):
        """Получение title с доски"""
        element = self.driver.find_element(
            By.CSS_SELECTOR,
            f'[data-rfd-draggable-id="{task_id}"]',
        )
        lines = self._extract_card_lines(element.text)
        return lines[0] if lines else ""

    def get_task_content(self, task_id):
        """Получение content с доски"""
        element = self.driver.find_element(
            By.CSS_SELECTOR,
            f'[data-rfd-draggable-id="{task_id}"]',
        )
        lines = self._extract_card_lines(element.text)
        return lines[1] if len(lines) > 1 else ""

    def wait_for_task_title(self, task_id, expected_title):
        """Ожидание появления title задачи"""
        locator = (
            By.CSS_SELECTOR,
            f'[data-rfd-draggable-id="{task_id}"]',
        )

        def title_matches(driver):
            element = driver.find_element(*locator)
            lines = self._extract_card_lines(element.text)
            return bool(lines and lines[0] == expected_title)

        self.wait.until(title_matches)

    def wait_for_task_absence(self, task_id):
        """Ожидание исчезновения задачи с доски."""
        locator = (
            By.CSS_SELECTOR,
            f'[data-rfd-draggable-id="{task_id}"]',
        )
        self.wait.until(lambda d: len(d.find_elements(*locator)) == 0)

    def get_task_ids_in_column(self, status_name):
        """
        Получение id видимых задач в конкретной колонке 
        для проверки статуса через положение на доске
        """
        elements = self.driver.find_elements(
            By.XPATH,
            f"//h6[text()='{status_name}']/following-sibling::div"
            "//div[@data-rfd-draggable-id]",
        )

        ids = []
        for element in elements:
            task_id = element.get_attribute("data-rfd-draggable-id")
            if task_id and task_id.isdigit():
                ids.append(int(task_id))

        return ids

    def is_task_in_column(self, task_id, status_name):
        """Проверка нахождения задачи в указанной колонке"""
        xpath = (
            f"//h6[text()='{status_name}']/following-sibling::div"
            f"//div[@data-rfd-draggable-id='{task_id}']"
        )

        try:
            self.driver.find_element(By.XPATH, xpath)
            return True
        except NoSuchElementException:
            return False

    # -----------------------------------------------------------------
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ДЛЯ SELECT / FILTER
    # -----------------------------------------------------------------

    def _get_combobox_by_input_name(self, input_name):
        """Поиск combobox рядом со скрытым input для фильтров и форм"""
        input_element = self.wait.until(
            EC.presence_of_element_located((By.NAME, input_name))
        )

        return input_element.find_element(
            By.XPATH,
            "../div[@role='combobox']",
        )

    def _click_visible_option(self, text):
        """
        Рефакторинг для CI т.к. option.click() иногда падает с
        ElementClickInterceptedException из-за анимаций/оверлеев MUI
        """
        option_xpath = (
            f"//li[@role='option' and normalize-space()='{text}']"
        )

        self.wait.until(
            lambda d: any(
                element.is_displayed()
                for element in d.find_elements(By.XPATH, option_xpath)
            )
        )

        last_error = None

        for _ in range(3):
            options = self.driver.find_elements(By.XPATH, option_xpath)
            visible_option = next(
                (element for element in options if element.is_displayed()),
                None,
            )

            if visible_option is None:
                continue

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                visible_option,
            )

            try:
                visible_option.click()
                time.sleep(0.3)
                return
            except (
                ElementClickInterceptedException,
                StaleElementReferenceException,
                TimeoutException,
            ) as error:
                last_error = error
                try:
                    self.driver.execute_script(
                        "arguments[0].click();",
                        visible_option,
                    )
                    time.sleep(0.3)
                    return
                except Exception as js_error:
                    last_error = js_error

        if last_error:
            raise last_error

        raise NoSuchElementException(f"Не найдена опция: {text}")

    # -----------------------------------------------------------------
    # ФИЛЬТРЫ
    # -----------------------------------------------------------------

    def select_filter(self, input_name, value):
        """
        Выбор значений фильтров
        input_name: assignee_id / status_id / label_id
        """
        combobox = self._get_combobox_by_input_name(input_name)

        self.wait.until(EC.element_to_be_clickable(combobox))
        combobox.click()

        self._click_visible_option(value)

        # Пауза UI для закрытия выпадающего списка
        time.sleep(0.5)

    def verify_filters_visible(self):
        """Проверка отображения фильтров"""
        filters = {
            self.filter_assignee_container: "Assignee",
            self.filter_status_container: "Status",
            self.filter_label_container: "Label",
        }

        for locator, expected_text in filters.items():
            element = self.wait.until(
                EC.visibility_of_element_located(locator)
            )
            assert expected_text in element.text, (
                f"Фильтр {expected_text} не найден или текст неверный"
            )

        return True

    # -----------------------------------------------------------------
    # СОЗДАНИЕ ЗАДАЧ
    # -----------------------------------------------------------------

    def select_option(self, input_name, text):
        """
        Выбор значений формы create/edit
        input_name: assignee_id / status_id / label_id
        """
        combobox = self._get_combobox_by_input_name(input_name)

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            combobox,
        )
        combobox.click()

        self._click_visible_option(text)

        # Закрытие выпадающего списка
        self.driver.switch_to.active_element.send_keys(Keys.ESCAPE)

    def create_task(self, assignee, title, content, status, labels):
        """Создание новой задачи"""
        self.wait.until(EC.element_to_be_clickable(self.btn_create)).click()

        self.select_option("assignee_id", assignee)

        self.wait.until(
            EC.visibility_of_element_located(self.input_name)
        ).send_keys(title)

        self.driver.find_element(*self.input_description).send_keys(content)

        self.select_option("status_id", status)

        for label in labels:
            self.select_option("label_id", label)

        self.wait.until(EC.element_to_be_clickable(self.btn_save)).click()

    # -----------------------------------------------------------------
    # РЕДАКТИРОВАНИЕ И УДАЛЕНИЕ
    # -----------------------------------------------------------------

    def clear_text_field(self, locator):
        """Очистка текстового поля через Ctrl+A + Backspace"""
        self.wait.until(EC.visibility_of_element_located(locator)).click()

        actions = ActionChains(self.driver)
        (
            actions
            .key_down(Keys.CONTROL)
            .send_keys("a")
            .key_up(Keys.CONTROL)
            .send_keys(Keys.BACKSPACE)
            .perform()
        )

    def clear_labels(self, current_labels):
        """
        Снятие текущих значений label
        """
        for label in current_labels:
            self.select_option("label_id", label)

    def update_task_fields(
        self,
        title=None,
        content=None,
        assignee=None,
        status=None,
        new_labels=None,
        old_labels=None,
    ):
        """Обновление поля задачи через edit-страницу"""
        if assignee:
            self.select_option("assignee_id", assignee)

        if title:
            self.clear_text_field(self.input_name)
            self.driver.find_element(*self.input_name).send_keys(title)

        if content:
            self.clear_text_field(self.input_description)
            self.driver.find_element(*self.input_description).send_keys(
                content
            )

        if status:
            self.select_option("status_id", status)

        if old_labels:
            self.clear_labels(old_labels)

        if new_labels:
            for label in new_labels:
                self.select_option("label_id", label)

        self.wait.until(EC.element_to_be_clickable(self.btn_save)).click()

    def delete_task(self):
        """Удаление задачи через show-страницу"""
        self.wait.until(EC.element_to_be_clickable(self.btn_delete)).click()

    # -----------------------------------------------------------------
    # ПЕРЕМЕЩЕНИЕ МЕЖДУ КОЛОНКАМИ
    # -----------------------------------------------------------------

    def move_task_to_status(self, task_id, target_status):
        """Смена колонки статуса задачи"""
        handle_xpath = (
            f'//div[@data-rfd-drag-handle-draggable-id="{task_id}"]'
        )
        column_xpath = (
            f"//h6[text()='{target_status}']"
            "/following-sibling::div[@data-rfd-droppable-id]"
        )

        source = self.wait.until(
            EC.presence_of_element_located((By.XPATH, handle_xpath))
        )
        target = self.wait.until(
            EC.presence_of_element_located((By.XPATH, column_xpath))
        )

        actions = ActionChains(self.driver)

        (
            actions
            .move_to_element(source)
            .click_and_hold(source)
            .pause(0.5)
            .move_by_offset(10, 10)
            .pause(1)
            .move_to_element(target)
            .pause(1)
            .release()
            .perform()
        )

        time.sleep(1)