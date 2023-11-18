
from logger import logger
from formFiller import FormFiller


def fill_form(driver, wait_time=10):

    try:
        form_filler = FormFiller(driver, wait_time)
        form_filler.fill_passport_number().select_nationality_option().click_search_button().wait_for_search_effect().find_and_click_checkbox().click_submit_in_production()
        logger.info("Form filling process completed.")
    except Exception as e:
        logger.error(f"Error during form filling process: {e}")
        raise
