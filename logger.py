import os
import logging
import watchtower
from logging.handlers import RotatingFileHandler

def setup_logger():
    # Define log level
    log_level = logging.INFO

    # Create a logger
    logger = logging.getLogger('FormFiller')
    logger.setLevel(log_level)

    # Check if the environment is development or production
    environment = os.getenv('ENVIRONMENT', 'development')

    if environment == 'development':
        # In development, log to a file
        handler = RotatingFileHandler('development.log', maxBytes=10000, backupCount=1)
    else:
        # In production, log to AWS CloudWatch
        handler = watchtower.CloudWatchLogHandler()

    # Set formatter for log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger


logger = setup_logger()