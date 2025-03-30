from extract import extract_data, print_data_stats
from transform import clean_data
from load import load_data
from logging_config import get_logger

logger = get_logger()


def main():
    logger.info("ETL Pipeline Started")

    # Extract
    df = extract_data()
    print_data_stats(df)
    if df is None:
        logger.error("Extraction failed. Exiting.")
        return

    # Transform
    df_clean = clean_data(df)
    if df_clean is None:
        logger.error("Transformation failed. Exiting.")
        return

    # Load
    load_data(df_clean)

    logger.info("ETL Pipeline Completed")


if __name__ == "__main__":
    main()
