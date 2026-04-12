import os

USER = {
    "login": "admin@google.com",
    "password": "admin1234567",
}

SIGN_IN_TEXT = "Sign in"
DASHBOARD_TITLE = "Welcome to the administration"

DEFAULT_TIMEOUT = int(os.getenv("SELENIUM_DEFAULT_TIMEOUT", "10"))
POLL_INTERVAL = float(os.getenv("SELENIUM_POLL_INTERVAL", "0.5"))
PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "45"))
IMPLICIT_WAIT = float(os.getenv("SELENIUM_IMPLICIT_WAIT", "0.2"))
WINDOW_SIZE = os.getenv("BROWSER_WINDOW_SIZE", "1920,1080")
