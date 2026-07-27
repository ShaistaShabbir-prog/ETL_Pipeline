"""
etl_pipeline/load.py

Data loading module — writes transformed data to output destination.

Supported targets:
- CSV file (default, no dependencies)
- PostgreSQL (requires psycopg2 + DATABASE_URL env var)
- SQLite (for local testing)
"""
from __future__ import annotations
import logging
import os
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


def load_to_csv(df: pd.DataFrame, output_path: str | Path, append: bool = False) -> Path:
    """
    Write DataFrame to CSV file.

    Args:
        df: Transformed DataFrame
        output_path: Output file path
        append: If True, append to existing file

    Returns:
        Path to written file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if (append and output_path.exists()) else "w"
    header = not (append and output_path.exists())
    df.to_csv(output_path, mode=mode, header=header, index=False)
    logger.info(f"Loaded {len(df):,} rows to {output_path}")
    return output_path


def load_to_sqlite(df: pd.DataFrame, db_path: str = "etl_output.db",
                   table_name: str = "events", if_exists: str = "replace") -> str:
    """
    Write DataFrame to SQLite database (great for local testing).

    Args:
        df: Transformed DataFrame
        db_path: Path to SQLite database file
        table_name: Table name to write to
        if_exists: 'replace', 'append', or 'fail'

    Returns:
        Connection string
    """
    import sqlite3
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    conn.close()
    logger.info(f"Loaded {len(df):,} rows to SQLite: {db_path}::{table_name}")
    return f"sqlite:///{db_path}"


def load_to_postgres(df: pd.DataFrame, table_name: str = "events",
                     if_exists: str = "append") -> bool:
    """
    Write DataFrame to PostgreSQL.

    Requires: DATABASE_URL environment variable
    e.g. DATABASE_URL=postgresql://user:pass@localhost:5432/etl_db
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
    try:
        from sqlalchemy import create_engine
        engine = create_engine(database_url)
        df.to_sql(table_name, engine, if_exists=if_exists, index=False, chunksize=1000)
        logger.info(f"Loaded {len(df):,} rows to PostgreSQL table '{table_name}'")
        return True
    except Exception as e:
        logger.error(f"PostgreSQL load failed: {e}")
        return False


def run_pipeline(source_csv: str = "data/sample_events.csv",
                 output_csv: str = "data/output/events_clean.csv") -> dict:
    """
    Convenience function: run full extract → transform → load pipeline.
    """
    from etl_pipeline.extract import extract_from_csv
    from etl_pipeline.transform import transform, validate

    logger.info("=== ETL Pipeline Start ===")
    df_raw    = extract_from_csv(source_csv)
    df_clean  = transform(df_raw)
    report    = validate(df_clean)
    out_path  = load_to_csv(df_clean, output_csv)
    also_sql  = load_to_sqlite(df_clean)

    result = {
        "rows_extracted": len(df_raw),
        "rows_loaded":    len(df_clean),
        "output_csv":     str(out_path),
        "output_sqlite":  also_sql,
        "validation":     report,
    }
    logger.info(f"=== ETL Pipeline Complete: {result} ===")
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s")
    result = run_pipeline()
    print("Result:", result)
