import os
import logging
import watchtower
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger():
    # Define log level
    log_level = logging.DEBUG
    LOGS_DIR = Path(__file__).resolve().parent.parent / 'logs'
    # Create a logger
    logger = logging.getLogger('FormFiller')
    logger.setLevel(log_level)

    # Check if the environment is development or production
    # environment = os.getenv('ENVIRONMENT', 'development')
    environment = 'development'

    if environment != 'production':
        # In development, log to a file
        handler = RotatingFileHandler(f"{LOGS_DIR}/development.log", maxBytes=10000, backupCount=1)
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