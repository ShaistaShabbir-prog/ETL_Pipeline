import pandas as pd
from loguru import logger

def clean_data(df):
    """Cleans and transforms the data."""
    try:
        # Standardize date format
        df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce").dt.strftime("%Y-%m-%d")

        # Remove duplicates
        df = df.drop_duplicates()

        # Handle missing values
        df = df.dropna(subset=["name", "date_of_birth"])

        # Convert salary to numeric
        df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

        logger.info(f"Transformed data: {df.shape[0]} records remain after cleaning.")
        return df
    except Exception as e:
        logger.error(f"Data transformation error: {e}")
        return None
