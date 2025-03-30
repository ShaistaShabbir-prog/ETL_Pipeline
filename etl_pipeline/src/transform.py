import pandas as pd
from loguru import logger


def clean_data(df):
    """Cleans and transforms the data."""
    try:
        # Standardize date format
        # df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce")
        # Standardize date format
        df["date_of_birth"] = pd.to_datetime(
            df["date_of_birth"], errors="coerce"
        ).dt.strftime("%Y-%m-%d")
        # Log invalid dates
        invalid_dates = df[df["date_of_birth"].isna()]
        if not invalid_dates.empty:
            logger.warning(f"⚠️ {len(invalid_dates)} records have invalid date formats.")

        # Keep rows with missing date_of_birth (instead of dropping everything)
        df = df.dropna(subset=["name"])

        # Drop duplicates (but keep unique IDs)
        df = df.drop_duplicates(subset=["name", "date_of_birth"])

        # Convert salary to numeric
        df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

        # Log invalid salaries
        invalid_salaries = df[df["salary"].isna()]
        if not invalid_salaries.empty:
            logger.warning(f"⚠️ {len(invalid_salaries)} records have invalid salaries.")

        # Fill missing salaries with median instead of 0
        df["salary"] = df["salary"].fillna(df["salary"].median())

        logger.info(
            f"✅ Transformed data: {df.shape[0]} records remain after cleaning."
        )
        print(df.describe())
        return df
    except Exception as e:
        logger.error(f"❌ Data transformation error: {e}")
        return None
