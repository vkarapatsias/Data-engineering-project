import os
from config.logging_config import setup_testing_logging, logger

setup_testing_logging()

# Configuration file for API credentials, database settings, etc.
# Schiphol Airport API credentials
SCHIPHOL_API_APP_ID = os.getenv("SCHIPHOL_API_APP_ID")
SCHIPHOL_API_APP_KEY = os.getenv("SCHIPHOL_API_APP_KEY")
SCHEMA_VERSION = "4"
DATA_WINDOW_HOURS = 1

# Database connection settings
DB_PREFIX = os.getenv("DB_PREFIX")
DB_IP_ADDRESS = os.getenv("DB_IP_ADDRESS")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DB_URI = f"{DB_PREFIX}://{DB_USER}:{DB_PASSWORD}@{DB_IP_ADDRESS}/{DB_NAME}"
logger.debug(DB_URI)

# S3 configuration
# TODO
AWS_ACCESS_KEY_ID = "access_key_id"
AWS_SECRET_ACCESS_KEY = "secret_access_key"
S3_BUCKET_NAME = "your_bucket_name"
S3_BASE_KEY = "_window_report.csv"
