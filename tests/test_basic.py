from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_application_renders(driver, base_url):
    driver.get(base_url)
    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'button[type="submit"]')
        )
    )
    assert element is not None
