import os
import pandas as pd
import yaml
import matplotlib.pyplot as plt
import seaborn as sns
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

    try:
        df = pd.read_csv(file_path)
        logger.info(f"Extracted {len(df)} records from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error extracting data: {e}")
        return None


def print_data_stats(df):
    """Prints basic statistics and identifies duplicates in the dataset."""
    if df is None or df.empty:
        logger.warning("No data available for statistics.")
        return

    logger.info("Generating data statistics...")

    # Print basic statistics
    logger.info("\n📊 **Basic Dataset Statistics:**")
    logger.info(df.describe(include="all"))  # Summary of numeric & categorical columns

    logger.info("\n🧐 **Missing Values:**")
    logger.info(df.isnull().sum())  # Missing values count

    # Check for duplicates
    duplicates = df[df.duplicated()]
    if not duplicates.empty:
        logger.info("\n⚠️ **Duplicate Records Found:**")
        print(duplicates)
    else:
        logger.info("\n✅ No duplicate records found.")

    logger.info("Data statistics generated successfully.")
