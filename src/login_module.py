import os
from dotenv import load_dotenv
load_dotenv()

from selenium.webdriver.common.by import By
from twocaptcha import TwoCaptcha
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from pathlib import Path

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

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'


def save_captcha_image(element: WebElement, filename="captcha.png"):
    path = f"{DATA_DIR}/{filename}"
    element.screenshot(path)
    logger.debug(f"Captcha image saved to {path}")
    return path


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
        logger.debug(f"Captcha solution entered. -> {captcha_solution}")
        return True
    else:
        logger.error("Failed to get captcha solution.")
        return False


def click_login_button(driver):
    try:
        login_button = driver.find_element(By.XPATH, LOGIN_BUTTON_XPATH)
        login_button.click()
        logger.debug("Login button clicked.")
    except Exception as e:
        logger.error(f"Error clicking login button: {e}")
        raise


def login(driver, email, password, api_key_2captcha, max_retries=5):
    success_url = f"{ROOT_URL}/#/home"
    navigate_to_login_page(driver)
    fill_login_credentials(driver, email, password)

    for attempt in range(max_retries):
        if enter_captcha_solution(driver, api_key_2captcha):
            click_login_button(driver)

            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(
                    (By.XPATH, INVALID_DATA_MESSAGE_XPATH)))
                logger.warning(
                    f"Invalid data error on attempt {attempt + 1}, retrying...")
                time.sleep(2)
                continue
            except TimeoutException:
                pass  # No error message, proceed to check for success URL

            try:
                WebDriverWait(driver, 10).until(EC.url_to_be(success_url))
                logger.info("Login successful.")
                return True
            except TimeoutException:
                logger.warning(
                    f"Captcha attempt {attempt + 1} failed, retrying...")
        else:
            continue

    logger.error("Maximum retries reached. Login failed.")
    return False
