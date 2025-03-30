from loguru import logger
import sys
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "etl.log")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure Loguru
logger.remove()  # Remove default logger
logger.add(
    sys.stdout, format="{time} {level} {message}", level="INFO"
)
logger.add(
    LOG_FILE, rotation="1 MB", retention="7 days", level="INFO", backtrace=True, diagnose=True
)

def get_logger():
    return logger
