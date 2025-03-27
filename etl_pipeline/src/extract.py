import os
import pandas as pd
import yaml
from logging_config import get_logger

logger = get_logger()

# Get the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load configuration
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.yaml")

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Correct way to get the absolute path of the CSV file
file_path = os.path.join(BASE_DIR, config["etl"]["data_path"])

def extract_data():
    """Extracts data from CSV file."""
    print(f"Looking for file at: {file_path}")  # Debugging line
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Extracted {len(df)} records from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error extracting data: {e}")
        return None
