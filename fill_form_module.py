from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
from logger import logger

# Constants
PASSPORT_FIELD_SELECTOR = "input[formcontrolname='passportNo']"
NATIONALITY_AUTOCOMPLETE_PANEL_SELECTOR = ".mat-autocomplete-panel"
NATIONALITY_OPTION_TEXT = 'ISR-ISRAELI'
SEARCH_BUTTON_XPATH = "//button[@mat-flat-button and .//mat-icon[text()='search']]"
TERMS_AND_CONDITIONS_CHECKBOX_XPATH = "//b[contains(text(), 'Terms and Conditions')]/ancestor::div[1]//mat-checkbox"
GIVEN_NAME_FIELD_SELECTOR = "input[formcontrolname='givenName']"
NATIONALITY_INPUT_XPATH = "//sit-label[.//span[text()='Nationality']]/following-sibling::sit-autocomplete//input"



def fill_passport_number(driver):
    try:
        passport = os.environ.get('PASSPORT_NUMBER')
        passport_field = driver.find_element(
            By.CSS_SELECTOR, PASSPORT_FIELD_SELECTOR)
        passport_field.send_keys(passport)
        logger.info("Filled in the passport number.")
    except NoSuchElementException as e:
        logger.error(f"Error in finding passport input element: {e}")
        raise


def find_and_fill_nationality_field(driver, nationality):
    try:
        input_field = driver.find_element(By.XPATH, NATIONALITY_INPUT_XPATH)
        input_field.send_keys(nationality)
        logger.info("Filled in the nationality field.")
    except NoSuchElementException as e:
        logger.error(f"Error in finding or filling nationality field: {e}")
        raise


def select_nationality_option(driver, wait_time):
    try:
        find_and_fill_nationality_field(driver, os.environ.get('NATIONALITY'))
        WebDriverWait(driver, wait_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, NATIONALITY_AUTOCOMPLETE_PANEL_SELECTOR)))
        options = driver.find_elements(By.CSS_SELECTOR, ".mat-option-text")
        for option in options:
            if option.text == NATIONALITY_OPTION_TEXT:
                option.click()
                logger.info(f"Selected nationality option: {NATIONALITY_OPTION_TEXT}")
                break
    except TimeoutException as e:
        logger.error("Timeout waiting for nationality options to appear.")
        raise
    except NoSuchElementException as e:
        logger.error("Error in selecting nationality option.")
        raise


def click_search_button(driver):
    try:
        search_button = driver.find_element(By.XPATH, SEARCH_BUTTON_XPATH)
        search_button.click()
        logger.info("Clicked the search button.")
    except NoSuchElementException as e:
        logger.error(f"Error in finding the search button: {e}")
        raise


def wait_for_search_effect(driver, wait_time):
    try:
        wait = WebDriverWait(driver, wait_time)
        wait.until(EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, GIVEN_NAME_FIELD_SELECTOR), ''))
        logger.info("Given name field has content.")
    except TimeoutException as e:
        logger.error("Timeout waiting for search effect.")
        raise


def scroll_into_view_and_click(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()
        logger.info("Clicked the element.")
    except Exception as e:
        logger.error(f"Error in scrolling into view and clicking: {e}")
        raise


def find_and_click_checkbox(driver):
    try:
        mat_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, TERMS_AND_CONDITIONS_CHECKBOX_XPATH))
        )
        # Wait for any potential overlays to disappear
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.CSS_SELECTOR, ".overlay"))
        )
        # Scroll into view and click
        scroll_into_view_and_click(driver, mat_checkbox)
    except TimeoutException:
        logger.error("Timeout while waiting for the checkbox or overlay to be ready.")
        raise
    except NoSuchElementException as e:
        logger.error(f"Error in finding the Terms and Conditions checkbox: {e}")
        raise



def fill_form(driver, wait_time=10):
    try:
        fill_passport_number(driver)
        select_nationality_option(driver, wait_time)
        click_search_button(driver)
        wait_for_search_effect(driver, wait_time)
        find_and_click_checkbox(driver)
        logger.info("Form filling process completed.")
    except Exception as e:
        logger.error(f"Error during form filling process: {e}")
        raise
