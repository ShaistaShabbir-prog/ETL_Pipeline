"""
etl_pipeline/transform.py

Data transformation module — clean, validate, enrich raw data.

Transformations applied:
1. Schema normalization (column names, types)
2. Null handling (drop rows missing critical fields)
3. String cleaning (strip whitespace, lowercase event_type)
4. Date parsing (standardize to YYYY-MM-DD)
5. Deduplication (on id column)
6. Enrichment (add _loaded_at timestamp)
"""
from __future__ import annotations
import logging
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"id", "event_type", "location", "event_date", "description"}


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run full transformation pipeline on raw DataFrame.

    Args:
        df: Raw DataFrame from extract step

    Returns:
        Cleaned, validated DataFrame ready for loading

    Raises:
        ValueError: If critical columns are missing
    """
    logger.info(f"Starting transform: {len(df):,} rows")
    df = df.copy()

    # ── 1. Column check ──────────────────────────────────────
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # ── 2. String normalization ──────────────────────────────
    for col in ["event_type", "location", "description"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df["event_type"] = df["event_type"].str.upper().str[:2]
    df["location"]   = df["location"].str.title()

    # ── 3. Date parsing ──────────────────────────────────────
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce").dt.date
    before = len(df)
    df = df.dropna(subset=["event_date"])
    if len(df) < before:
        logger.warning(f"Dropped {before - len(df)} rows with unparseable dates")

    # ── 4. Drop null critical fields ─────────────────────────
    before = len(df)
    df = df.dropna(subset=["id", "event_type"])
    df = df[df["id"].astype(str).str.strip() != ""]
    if len(df) < before:
        logger.warning(f"Dropped {before - len(df)} rows with null id/event_type")

    # ── 5. Deduplication ────────────────────────────────────
    before = len(df)
    df = df.drop_duplicates(subset=["id"])
    dupes = before - len(df)
    if dupes:
        logger.info(f"Removed {dupes} duplicate records")

    # ── 6. Enrichment ────────────────────────────────────────
    df["_loaded_at"] = datetime.now().isoformat()
    df = df.reset_index(drop=True)

    logger.info(f"Transform complete: {len(df):,} rows (from {before})")
    return df


def validate(df: pd.DataFrame) -> dict:
    """
    Run basic data quality checks. Returns a validation report dict.
    """
    report = {
        "total_rows":    len(df),
        "null_counts":   df.isnull().sum().to_dict(),
        "duplicate_ids": int(df["id"].duplicated().sum()) if "id" in df.columns else "N/A",
        "event_types":   df["event_type"].value_counts().to_dict() if "event_type" in df.columns else {},
        "date_range": {
            "min": str(df["event_date"].min()) if "event_date" in df.columns else "N/A",
            "max": str(df["event_date"].max()) if "event_date" in df.columns else "N/A",
        },
        "passed": True,
    }
    # Fail if too many nulls in critical columns
    for col in ["id", "event_type", "event_date"]:
        null_count = report["null_counts"].get(col, 0)
        if null_count / max(len(df), 1) > 0.05:
            report["passed"] = False
            report["fail_reason"] = f"Column '{col}' has {null_count} nulls (>{5}%)"
    return report
