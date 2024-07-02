# Configuration file for API credentials, database settings, etc.
# Schiphol Airport API credentials
SCHIPHOL_API_APP_ID = "c9c037a0"
SCHIPHOL_API_APP_KEY = "3a4afe525de0be736d70654b726893de"
SCHEMA_VERSION = "4"
DATA_WINDOW_HOURS = 0.5

# Database connection settings
DB_PREFIX = "postgresql+psycopg2://"
DB_IP_ADDRESS = "localhost"
DB_USER = "my_user"
DB_PASSWORD = "my_password"
DB_NAME = "schiphol_airport_db"
DB_URI = DB_PREFIX + DB_USER + ":" + DB_PASSWORD + "@" + DB_IP_ADDRESS + "/" + DB_NAME

# S3 configuration
AWS_ACCESS_KEY_ID = "access_key_id"
AWS_SECRET_ACCESS_KEY = "secret_access_key"
S3_BUCKET_NAME = "your_bucket_name"
S3_BASE_KEY = "_window_report.csv"
