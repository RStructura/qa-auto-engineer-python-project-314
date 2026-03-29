import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.event_firing_webdriver import (
    EventFiringWebDriver,
)
from selenium.webdriver.support.events import AbstractEventListener

from pages.login_page import LoginPage


# Работа с Chrome
@pytest.fixture
def driver():
    options = Options()

    # Настройка виртуального окна
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Отключение плашки об автоматизации
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Отключение проверки паролей и окна сохранения
    prefs = {
        "credentials_enable_service": False, 
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    
    # Запуск браузера
    raw_driver = webdriver.Chrome(options=options)
    
    # Замедление драйвера
    driver = EventFiringWebDriver(raw_driver, SlowMotionListener())
    
    # Завершение
    yield driver
    driver.quit()


# Замедление выполнения тестов
class SlowMotionListener(AbstractEventListener):
    # Пауза после каждого клика
    def after_click(self, element, driver):
        time.sleep(0.5)
    
    # Пауза после каждого ввода текста
    def after_change_value_of(self, element, driver):
        time.sleep(0.5)


# Фикстура: Базовый URL
@pytest.fixture
def base_url():
    env_url = os.getenv("APP_BASE_URL")
    if env_url:
        return env_url

    if os.path.exists("/.dockerenv"):
        return "http://server"

    return "http://localhost:5173"


# Фикстура: Авторизация
@pytest.fixture
def auth_driver(driver, base_url):
    driver.get(base_url)
    login_page = LoginPage(driver)
    login_page.login("admin@google.com", "admin1234567")
    return driver


def pytest_configure(config):
    markers = [
        "smoke: smoke test",
        "step_3: auth test",

        "step_4_viewList: users list test",
        "step_4_createUser: users create test",
        "step_4_editUser: users edit test",
        "step_4_deleteOne: users delete one test",
        "step_4_deleteAll: users delete all test",

        "step_5_viewList: statuses list test",
        "step_5_createStatus: statuses create test",
        "step_5_editStatus: statuses edit test",
        "step_5_deleteOne: statuses delete one test",
        "step_5_deleteAll: statuses delete all test",

        "step_6_viewList: labels list test",
        "step_6_createLabel: labels create test",
        "step_6_editLabel: labels edit test",
        "step_6_deleteOne: labels delete one test",
        "step_6_deleteAll: labels delete all test",
        
        "step_7_viewBoard: tasks board test",
        "step_7_filtersTasks: tasks filter test",
        "step_7_createTasks: tasks create test",
        "step_7_editTasks: tasks edit test",
        "step_7_dragAndDropTasks: tasks dnd test",
        "step_7_deleteTasks: tasks delete test",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)