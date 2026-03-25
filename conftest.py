import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def driver():
    options = Options()
    # Стандартные настройки для стабильности в контейнерах
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Проверяем, пришел ли URL удаленного сервера извне
    remote_url = os.getenv('SELENIUM_REMOTE_URL')

    if remote_url:
        # Если URL есть (в Docker/CI), подключаемся удаленно
        driver = webdriver.Remote(
            command_executor=remote_url,
            options=options
        )
    else:
        # Если URL нет (локально), запускаем обычный Chrome
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    yield driver
    driver.quit()


@pytest.fixture
def base_url():
    return os.getenv('APP_BASE_URL', 'http://localhost:5173')


@pytest.fixture
def auth_driver(driver, base_url):
    from pages.login_page import LoginPage
    login_page = LoginPage(driver)
    driver.get(f"{base_url}/#/login")
    login_page.login("admin@google.com", "admin1234567")
    return driver