import os
from config.logging_config import logger

# Schiphol Airport API credentials
SCHIPHOL_API_APP_ID = os.getenv("SCHIPHOL_API_APP_ID")
SCHIPHOL_API_APP_KEY = os.getenv("SCHIPHOL_API_APP_KEY")

# Expected data schema
SCHEMA_VERSION = "4"
# Window during which we fetch data, (it can also be a float e.g. 0.1 = 6 min)
if os.getenv("DATA_WINDOW_HOURS"):
    DATA_WINDOW_HOURS = float(
        os.getenv("DATA_WINDOW_HOURS")
    )  # ensure this is a float number
else:
    DATA_WINDOW_HOURS = 4
    logger.warning(
        f"DATA_WINDOW_HOURS was set automatically to {DATA_WINDOW_HOURS} hours."
    )
    logger.warning("To configure it use the environment variable 'DATA_WINDOW_HOURS'.")


# Database connection settings
DB_PREFIX = os.getenv("DB_PREFIX")
DB_IP_ADDRESS = os.getenv("DB_IP_ADDRESS")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DB_URI = f"{DB_PREFIX}://{DB_USER}:{DB_PASSWORD}@{DB_IP_ADDRESS}/{DB_NAME}"
logger.debug(f"Database URI is : {DB_URI}")

# S3 configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_BASE_KEY = "_window_report.csv"
