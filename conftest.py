from __future__ import annotations

import logging
import re
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from tests.config import TestConfig, load_config
from tests.utils.logging import configure_logging


def _ensure_basic_logging(level: str) -> None:
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=level)


@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    return load_config()


@pytest.fixture(scope="session")
def test_logger(test_config: TestConfig) -> logging.Logger:
    _ensure_basic_logging(test_config.log_level)
    logger = configure_logging(
        test_config.log_level,
        test_config.log_dir,
    )
    logging.captureWarnings(True)
    logger.info(
        "Logging initialised "
        "(implementation=%s, base_url=%s, log_dir=%s)",
        test_config.implementation or "custom",
        test_config.base_url,
        test_config.log_dir,
    )
    return logger


@pytest.fixture(scope="session")
def base_url(test_config: TestConfig) -> str:
    return test_config.base_url


def _configure_options(test_config: TestConfig) -> Options:
    options = Options()
    if test_config.headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--window-size={test_config.window_size}")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"],
    )
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        },
    )

    chrome_binary = test_config.chrome_binary
    if chrome_binary and Path(chrome_binary).exists():
        options.binary_location = chrome_binary

    return options


def _prepare_driver(
    driver: webdriver.Chrome,
    base_url: str,
) -> None:
    driver.get(base_url)
    driver.delete_all_cookies()
    driver.execute_script(
        "window.localStorage.clear(); window.sessionStorage.clear();",
    )


def _new_browser(
    base_url: str,
    test_config: TestConfig,
) -> webdriver.Chrome:
    options = _configure_options(test_config)
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(test_config.page_load_timeout)
    driver.implicitly_wait(test_config.implicit_wait)
    _prepare_driver(driver, base_url)
    return driver


def _safe_test_name(nodeid: str) -> str:
    name = nodeid.replace("::", "__").replace("/", "_")
    return re.sub(r"[^\w.-]", "_", name)


def _save_screenshot(
    driver: webdriver.Chrome,
    target_dir: Path,
    nodeid: str,
    logger: logging.Logger,
) -> None:
    filename = f"{_safe_test_name(nodeid)}.png"
    path = target_dir / filename
    try:
        success = driver.save_screenshot(str(path))
    except Exception as error:  # noqa: BLE001
        logger.error("Failed to create screenshot %s: %s", path, error)
        return

    if success:
        logger.info("Saved screenshot to %s", path)
    else:
        logger.warning(
            "Driver did not report success when saving screenshot to %s",
            path,
        )


@pytest.fixture
def driver(
    base_url: str,
    test_config: TestConfig,
    test_logger: logging.Logger,
    request: pytest.FixtureRequest,
):
    test_logger.debug(
        "Creating new browser instance for %s",
        request.node.nodeid,
    )
    browser = _new_browser(base_url, test_config)
    try:
        yield browser
    finally:
        outcome = getattr(request.node, "rep_call", None)
        if outcome and outcome.failed:
            _save_screenshot(
                browser,
                test_config.screenshots_dir,
                request.node.nodeid,
                test_logger,
            )
        test_logger.debug(
            "Closing browser instance for %s",
            request.node.nodeid,
        )
        browser.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo,
):
    outcome = yield
    result = outcome.get_result()
    setattr(item, f"rep_{result.when}", result)
