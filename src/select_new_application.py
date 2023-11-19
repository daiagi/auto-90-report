
import os
from logger import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
load_dotenv()


ROOT_URL = os.environ.get('ROOT_URL')
fill_form_url = f"{ROOT_URL}/#/requestfrm/add"

NEW_APPLICATION_BUTTON_XPATH = "//button[.//span[contains(text(), 'NEW APPLICATION')]]"
CLOSE_BUTTON_XPATH = "//button[.//span[contains(text(), 'Close')]]"


def click_new_application_button(driver):
    try:
        new_application_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, NEW_APPLICATION_BUTTON_XPATH))
        )
        new_application_button.click()
        logger.debug("Clicked on the NEW APPLICATION button.")
    except TimeoutException as e:
        logger.error("Failed to find or click the NEW APPLICATION button.")
        raise


def wait_for_form_ready(driver):
    try:
        WebDriverWait(driver, 10).until(
            lambda d: d.current_url == fill_form_url)
        logger.debug("Arrived at the form URL")

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, CLOSE_BUTTON_XPATH))
        )
        logger.debug("Close button is now visible.")
    except TimeoutException as e:
        logger.error(
            "Failed to navigate to the form URL or close button not visible.")
        raise


def select_new_application(driver):
    logger.info("Starting new application process.")
    try:
        click_new_application_button(driver)
        wait_for_form_ready(driver)
        logger.info("Ready to fill form.")
    except Exception as e:
        logger.error(f"Error during new application process: {e}")
        raise
