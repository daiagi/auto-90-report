import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from logger import logger


from login_module import login
from fill_form_module import fill_form
from select_new_application import select_new_application

load_dotenv()

# Environment Variables
email = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
api_key_2captcha = os.environ.get('APIKEY_2CAPTCHA')


def create_webdriver_instance():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # If Chromedriver is in the PATH, you don't need to specify the executable_path
    driver = webdriver.Chrome(options=chrome_options)
    return driver

try:
    driver = create_webdriver_instance()
    login(driver, email, password, api_key_2captcha)
    select_new_application(driver)
    fill_form(driver)

finally:
    driver.quit()
    logger.info("Driver quit.")
