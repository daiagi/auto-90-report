import os
from selenium import webdriver
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
from logger import logger


from login_module import login
from fill_form_module import fill_form
from select_new_application import select_new_application

load_dotenv()

# Environment Variables
email = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
api_key_2captcha = os.environ.get('APIKEY_2CAPTCHA')

try:
    path = ChromeDriverManager().install()
    driver = webdriver.Chrome()
    login(driver, email, password, api_key_2captcha)
    select_new_application(driver)
    fill_form(driver)

finally:
    driver.quit()
    logger.info("Driver quit.")
