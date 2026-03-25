import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.event_firing_webdriver import (
    EventFiringWebDriver,
)
from selenium.webdriver.support.events import AbstractEventListener
from webdriver_manager.chrome import ChromeDriverManager

from pages.login_page import LoginPage


# Работа с Chrome
@pytest.fixture
def driver():
    options = Options()

    # Настройка виртуального окна
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")

    # Отключение плашки об автоматизации
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Отключение проверки паролей и окна сохранения
    prefs = {"credentials_enable_service": False, 
        "profile.password_manager_enabled": False}
    options.add_experimental_option("prefs", prefs)
    
    # Проверка актуальности версии браузера и его открытие
    service = Service(ChromeDriverManager().install())
    raw_driver = webdriver.Chrome(service=service, options=options)
    
    # Замедление драйвера
    driver = EventFiringWebDriver(raw_driver, SlowMotionListener())
    
    # Завершение
    yield driver
    driver.quit()


# Замедление выполнения тестов
class SlowMotionListener(AbstractEventListener):
    # Пауза после каждого клика
    def after_click(self, element, driver):
        time.sleep(0.3)
    
    # Пауза после каждого ввода текста
    def after_change_value_of(self, element, driver):
        time.sleep(0.3)


# Фикстура: Базовый URL
@pytest.fixture
def base_url():
    return os.getenv('APP_BASE_URL', 'http://localhost:5173')


# Фикстура: Авторизация
@pytest.fixture
def auth_driver(driver, base_url):
    login_page = LoginPage(driver)
    driver.get(base_url)
    login_page.login("admin@google.com", "admin1234567")
    return driver

