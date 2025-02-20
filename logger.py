import logging
import os
from logging.handlers import RotatingFileHandler
from starlette.config import Config
from datetime import datetime

# Load environment variables
config = Config(".env")  # Automatically loads variables from .env file

# Get today's date in YYYY-MM-DD format
today_date = datetime.now().strftime("%Y-%m-%d")

# Read values
LOG_FILE_PATTERN = config("LOG_FILE_PATTERN", default="adminlogs_{date}.log")
LOG_FILE = LOG_FILE_PATTERN.format(date=today_date)
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOG_MAX_SIZE = config("LOG_MAX_SIZE", cast=int, default=5)  # Convert MB to bytes
LOG_BACKUP_COUNT = config("LOG_BACKUP_COUNT", cast=int, default=3)
LOG_FORMAT = config("LOG_FORMAT", default="%(asctime)s - %(levelname)s - %(message)s")

# Create a logger
logger = logging.getLogger("my_project_logger")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# Configure Rotating File Handler
handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAX_SIZE, backupCount=LOG_BACKUP_COUNT)
formatter = logging.Formatter(LOG_FORMAT)
handler.setFormatter(formatter)

# Prevent duplicate logging
if not logger.hasHandlers():
    logger.addHandler(handler)
