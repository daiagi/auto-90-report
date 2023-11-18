import os

from selenium.webdriver.common.by import By
from twocaptcha import TwoCaptcha
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from logger import logger

# Root URL
ROOT_URL = os.environ.get('ROOT_URL')

# XPath and other selectors
EMAIL_INPUT_ID = 'mat-input-0'
PASSWORD_INPUT_ID = 'mat-input-1'
CAPTCHA_IMAGE_ID = 'angularBasicCaptchas_CaptchaImage'
CAPTCHA_INPUT_ID = 'captchaCodes'
LOGIN_BUTTON_XPATH = "//button[.//span[contains(text(), ' L O G I N ')]]"
INVALID_DATA_MESSAGE_XPATH = "//snack-bar-container/span[contains(text(), 'Invalid Data')]"



def save_captcha_image(element, filename="captcha.png"):
    element.screenshot(filename)
    return filename


def solve_captcha(image_path, api_key):
    solver = TwoCaptcha(api_key)
    try:
        result = solver.normal(image_path)
        return result.get('code')
    except Exception as e:
        print(f"Error solving CAPTCHA: {e}")
        return None
    
def navigate_to_login_page(driver):
    driver.get(f"{ROOT_URL}/#/login")
    logger.info("Navigated to the login page.")

def fill_login_credentials(driver, email, password):
    time.sleep(2)  # Wait for elements to load
    driver.find_element(By.ID, EMAIL_INPUT_ID).send_keys(email)
    driver.find_element(By.ID, PASSWORD_INPUT_ID).send_keys(password)
    logger.debug("Email and password fields filled.")

def enter_captcha_solution(driver, api_key_2captcha):
    captcha_image_element = driver.find_element(By.ID, CAPTCHA_IMAGE_ID)
    captcha_image_path = save_captcha_image(captcha_image_element)
    captcha_solution = solve_captcha(captcha_image_path, api_key_2captcha)
    if captcha_solution:
        captcha_input_field = driver.find_element(By.ID, CAPTCHA_INPUT_ID)
        captcha_input_field.clear()
        captcha_input_field.send_keys(captcha_solution)
        logger.debug("Captcha solution entered.")
        return True
    else:
        logger.error("Failed to get captcha solution.")
        return False

def click_login_button(driver):
    login_button = driver.find_element(By.XPATH, LOGIN_BUTTON_XPATH)
    login_button.click()
    logger.debug("Login button clicked.")


def login(driver, email, password, api_key_2captcha, max_retries=5):
    success_url = f"{ROOT_URL}/#/home"
    navigate_to_login_page(driver)
    fill_login_credentials(driver, email, password)

    for attempt in range(max_retries):
        if enter_captcha_solution(driver, api_key_2captcha):
            click_login_button(driver)

            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, INVALID_DATA_MESSAGE_XPATH)))
                logger.warning(f"Invalid data error on attempt {attempt + 1}, retrying...")
                time.sleep(2)
                continue
            except TimeoutException:
                pass  # No error message, proceed to check for success URL

            try:
                WebDriverWait(driver, 10).until(EC.url_to_be(success_url))
                logger.info("Login successful.")
                return True
            except TimeoutException:
                logger.warning(f"Captcha attempt {attempt + 1} failed, retrying...")
        else:
            continue

    logger.error("Maximum retries reached. Login failed.")
    return False

