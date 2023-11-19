from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement

import os
from logger import logger
from dotenv import load_dotenv
load_dotenv()

# Constants
PASSPORT_FIELD_SELECTOR = "input[formcontrolname='passportNo']"
NATIONALITY_AUTOCOMPLETE_PANEL_SELECTOR = ".mat-autocomplete-panel"
NATIONALITY_OPTION_TEXT = 'ISR-ISRAELI'
SEARCH_BUTTON_XPATH = "//button[@mat-flat-button and .//mat-icon[text()='search']]"
TERMS_AND_CONDITIONS_CHECKBOX_XPATH = "//b[contains(text(), 'Terms and Conditions')]/ancestor::div[1]//mat-checkbox"
GIVEN_NAME_FIELD_SELECTOR = "input[formcontrolname='givenName']"
NATIONALITY_INPUT_XPATH = "//sit-label[.//span[text()='Nationality']]/following-sibling::sit-autocomplete//input"
SUBMIT_BUTTON_XPATH = "//button[.//span[contains(text(), 'Submit')]]"
CONFIRM_BUTTON_XPATH = "//app-confirm-dialog//button[.//span[contains(text(), 'Confirm')]]"


class FormFiller:
    def __init__(self, driver, wait_time=10):
        self.driver = driver
        self.wait_time = wait_time
        logger.info("FormFiller initialized.")

    def fill_passport_number(self):
        passport = os.environ.get('PASSPORT_NUMBER')
        try:
            passport_field = self.driver.find_element(By.CSS_SELECTOR, PASSPORT_FIELD_SELECTOR)
            passport_field.send_keys(passport)
            logger.info("Filled in the passport number.")
        except NoSuchElementException as e:
            logger.error(f"Error in finding passport input element: {e}")
            raise
        return self  # Return self for chaining

    def find_and_fill_nationality_field(self, nationality):
        try:
            input_field = self.driver.find_element(By.XPATH, NATIONALITY_INPUT_XPATH)
            input_field.send_keys(nationality)
            logger.info("Filled in the nationality field.")
        except NoSuchElementException as e:
            logger.error(f"Error in finding or filling nationality field: {e}")
            raise
        return self

    def select_nationality_option(self):
        try:
            self.find_and_fill_nationality_field(os.environ.get('NATIONALITY'))
            WebDriverWait(self.driver, self.wait_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, NATIONALITY_AUTOCOMPLETE_PANEL_SELECTOR)))
            options = self.driver.find_elements(By.CSS_SELECTOR, ".mat-option-text")
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
        return self

    def click_search_button(self):
        try:
            search_button = self.driver.find_element(By.XPATH, SEARCH_BUTTON_XPATH)
            search_button.click()
            logger.info("Clicked the search button.")
        except NoSuchElementException as e:
            logger.error(f"Error in finding the search button: {e}")
            raise
        return self


    def wait_for_search_effect(self):
        try:
            wait = WebDriverWait(self.driver, self.wait_time)
            wait.until(EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, GIVEN_NAME_FIELD_SELECTOR), ''))
            logger.info("Given name field has content.")
        except TimeoutException as e:
            logger.error("Timeout waiting for search effect.")
            raise
        return self


    def scroll_into_view_and_click(self, element: WebElement):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
            logger.info(f"Clicked on element: {element.tag_name}")
        except Exception as e:
            logger.error(f"Error in scrolling into view and clicking: {e}")
            raise
        return self


    def find_and_click_checkbox(self):
        try:
            mat_checkbox = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, TERMS_AND_CONDITIONS_CHECKBOX_XPATH))
            )
            # Wait for any potential overlays to disappear
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element((By.CSS_SELECTOR, ".overlay"))
            )
            # Scroll into view and click
            self.scroll_into_view_and_click(mat_checkbox)
        except TimeoutException:
            logger.error("Timeout while waiting for the checkbox or overlay to be ready.")
            raise
        except NoSuchElementException as e:
            logger.error(f"Error in finding the Terms and Conditions checkbox: {e}")
            raise
        return self

    def click_submit_in_production(self):
        environment = os.getenv('ENVIRONMENT', 'development')
        if environment.lower() == 'production':
            try:
                submit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, SUBMIT_BUTTON_XPATH))
                )
                submit_button.click()
                logger.info("Clicked the Submit button in production.")
                return PostSubmitActions(self.driver, self.wait_time) 
            except TimeoutException:
                logger.error("Timeout while waiting for the Submit button to be clickable.")
                raise
            except NoSuchElementException:
                logger.error("Error in finding the Submit button.")
            return self



class PostSubmitActions:
    def __init__(self, driver, wait_time=10):
        self.driver = driver
        self.wait_time = wait_time

    def click_confirm(self):
        try:
            confirm_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, CONFIRM_BUTTON_XPATH))
            )
            confirm_button.click()
            logger.info("Clicked the Confirm button.")
        except NoSuchElementException as e:
            logger.error(f"Error in finding the Confirm button: {e}")
            raise
        return self
    
    def wait_for_pdf_page(self):
        try:
            extended_wait_time = 30  
            WebDriverWait(self.driver, extended_wait_time).until(
                lambda d: d.current_url.startswith("blob:")
            )
            logger.info("PDF page loaded. Application finished successfully.")
        except TimeoutException:
            logger.error("Timeout occurred waiting for the PDF page to load.")
            raise

