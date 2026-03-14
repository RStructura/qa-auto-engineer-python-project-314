from selenium.webdriver.common.by import By


class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_field = (By.NAME, "username")
        self.password_field = (By.NAME, "password")
        self.login_button = (By.CSS_SELECTOR, "button[type='submit']")
        self.profile_menu = (By.CSS_SELECTOR, 'button[aria-label="Profile"]')
        self.logout_button = (By.XPATH, "//li[contains(., 'Logout')]")

    def login(self, username, password):
        self.driver.find_element(*self.username_field).send_keys(username)
        self.driver.find_element(*self.password_field).send_keys(password)
        self.driver.find_element(*self.login_button).click()

    def logout(self):
        self.driver.find_element(*self.profile_menu).click()
        self.driver.find_element(*self.logout_button).click()
