import os
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.event_firing_webdriver import (
    EventFiringWebDriver,
)
from selenium.webdriver.support.events import AbstractEventListener

from pages.login_page import LoginPage

# Папка для артефактов падений
ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

# Управление режимами через переменные окружения
HEADLESS_ENABLED = os.getenv("HEADLESS", "1") == "1"
SLOWMO_ENABLED = os.getenv("SLOWMO", "0") == "1"


def _unwrap_driver(driver):
    return getattr(driver, "wrapped_driver", driver)


class SlowMotionListener(AbstractEventListener):
    def after_click(self, element, driver):
        time.sleep(0.3)

    def after_change_value_of(self, element, driver):
        time.sleep(0.3)


@pytest.fixture
def driver():
    options = Options()

    # Headless можно выключить так: HEADLESS=0
    if HEADLESS_ENABLED:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Логи браузера
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    # Отключение плашки об автоматизации
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # Отключение проверки паролей и окна сохранения
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)

    raw_driver = webdriver.Chrome(options=options)

    # Slow motion можно включить так: SLOWMO=1
    if SLOWMO_ENABLED:
        driver_instance = EventFiringWebDriver(
            raw_driver,
            SlowMotionListener(),
        )
    else:
        driver_instance = raw_driver

    yield driver_instance

    browser = _unwrap_driver(driver_instance)
    browser.quit()


@pytest.fixture
def base_url():
    env_url = os.getenv("APP_BASE_URL")
    if env_url:
        return env_url

    if os.path.exists("/.dockerenv"):
        return "http://server"

    return "http://localhost:5173"


@pytest.fixture
def auth_driver(driver, base_url):
    driver.get(base_url)
    login_page = LoginPage(driver)
    login_page.login("admin@google.com", "admin1234567")
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    setattr(item, f"rep_{report.when}", report)

    if report.when != "call" or not report.failed:
        return

    driver_instance = (
        item.funcargs.get("driver") or item.funcargs.get("auth_driver")
    )
    if driver_instance is None:
        return

    browser = _unwrap_driver(driver_instance)

    test_dir = ARTIFACTS_DIR / item.name
    test_dir.mkdir(parents=True, exist_ok=True)

    browser.save_screenshot(str(test_dir / "failure.png"))

    html_path = test_dir / "page_source.html"
    html_path.write_text(browser.page_source, encoding="utf-8")

    try:
        logs = browser.get_log("browser")
    except Exception:
        logs = []

    log_path = test_dir / "browser.log"
    log_path.write_text(
        "\n".join(str(entry) for entry in logs),
        encoding="utf-8",
    )


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