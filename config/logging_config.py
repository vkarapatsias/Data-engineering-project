import logging.config
import os

# Directory for log files
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure the directory exists


def setup_logging(log_filename="app.log", log_level=logging.INFO):
    """
    Setup logging configuration.

    Parameters:
    - log_filename: Name of the log file.
    - log_level: Logging level (default: INFO).
    """
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
            "file": {
                "level": "DEBUG",
                "formatter": "standard",
                "class": "logging.FileHandler",
                "filename": os.path.join(LOG_DIR, log_filename),
                "mode": "a",  # Append mode
            },
        },
        "loggers": {
            "": {
                "handlers": [
                    "console",
                    "file",
                ],  # Include both console and file handlers
                "level": log_level,
                "propagate": True,
            },
        },
    }

    # Configure logging based on settings in logging_config
    logging.config.dictConfig(logging_config)

    # Return the logger instance
    return logging.getLogger(__name__)


# Initialize the logger with default configuration
logger = setup_logging()


# Function to get a logger for testing (separate log file)
def setup_testing_logging():
    return setup_logging(log_filename="app.test.log", log_level=logging.DEBUG)
