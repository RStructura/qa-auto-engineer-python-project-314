from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from .constants import IMPLICIT_WAIT, PAGE_LOAD_TIMEOUT, WINDOW_SIZE


@dataclass(frozen=True, slots=True)
class TestConfig:
    implementation: str | None
    base_url: str
    log_level: str
    log_dir: Path
    screenshots_dir: Path
    headless: bool
    window_size: str
    page_load_timeout: int
    implicit_wait: float
    chrome_binary: str | None


def _resolve_path(value: str) -> Path:
    path = Path(value)
    try:
        return path.resolve()
    except OSError:
        return Path.cwd() / path


def load_config() -> TestConfig:
    implementation = os.getenv("IMPLEMENTATION")

    if implementation:
        base_url = f"http://{implementation}.test"
        descriptor = implementation
    else:
        base_url = os.getenv("APP_BASE_URL", "http://localhost:5173")
        parsed = urlparse(base_url)
        descriptor = parsed.hostname or "custom"

    log_level = os.getenv("TEST_LOG_LEVEL", "INFO").upper()
    log_dir = _resolve_path(os.getenv("TEST_LOG_DIR", "test-results"))
    log_dir.mkdir(parents=True, exist_ok=True)

    screenshots_dir = log_dir / "screenshots" / descriptor
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    headless = os.getenv("HEADLESS", "true").lower() not in {
        "false",
        "0",
        "no",
    }
    window_size = os.getenv("BROWSER_WINDOW_SIZE", WINDOW_SIZE)
    page_load_timeout = int(
        os.getenv("PAGE_LOAD_TIMEOUT", str(PAGE_LOAD_TIMEOUT))
    )
    implicit_wait = float(
        os.getenv("SELENIUM_IMPLICIT_WAIT", str(IMPLICIT_WAIT))
    )
    chrome_binary = os.getenv("CHROME_BIN", "/usr/bin/chromium")

    return TestConfig(
        implementation=implementation,
        base_url=base_url,
        log_level=log_level,
        log_dir=log_dir,
        screenshots_dir=screenshots_dir,
        headless=headless,
        window_size=window_size,
        page_load_timeout=page_load_timeout,
        implicit_wait=implicit_wait,
        chrome_binary=chrome_binary,
    )
