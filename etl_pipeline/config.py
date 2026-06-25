"""Fix for issue #2: config settings module."""
import os

DB_CONN     = os.getenv("DB_CONN",     "postgresql://user:pass@localhost:5432/etl_db")
SOURCE_CSV  = os.getenv("SOURCE_CSV",  "data/raw/source.csv")
OUTPUT_DIR  = os.getenv("OUTPUT_DIR",  "data/processed/")
LOG_LEVEL   = os.getenv("LOG_LEVEL",   "INFO")
BATCH_SIZE  = int(os.getenv("BATCH_SIZE", "1000"))
NULL_THRESHOLD = float(os.getenv("NULL_THRESHOLD", "0.3"))  # reject rows with >30% nulls
DATE_FORMAT = os.getenv("DATE_FORMAT", "%Y-%m-%d")
