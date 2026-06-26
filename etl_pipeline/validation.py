"""
Issue #10: Data validation with Pandera schema checks before load step.
"""
from __future__ import annotations
import logging
from typing import Any
import pandas as pd

log = logging.getLogger(__name__)


def get_schema():
    """Return Pandera schema for the ETL source data."""
    try:
        import pandera as pa
        schema = pa.DataFrameSchema({
            "id": pa.Column(int, nullable=False,
                            checks=pa.Check.greater_than(0)),
            "email": pa.Column(str, nullable=True,
                               checks=pa.Check.str_matches(r".+@.+\..+"),
                               coerce=True),
            "age": pa.Column(float, nullable=True,
                             checks=[pa.Check.ge(0), pa.Check.le(120)]),
            "date": pa.Column(str, nullable=True),
        }, coerce=True)
        return schema
    except ImportError:
        log.warning("pandera not installed — pip install pandera")
        return None


def validate(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """
    Validate DataFrame against schema.
    Returns (valid_df, error_report).
    """
    schema = get_schema()
    errors: list[dict] = []

    if schema is None:
        # Fallback: manual validation
        return _manual_validate(df)

    try:
        import pandera as pa
        valid_df = schema.validate(df, lazy=True)
        log.info("Validation passed: %d rows", len(valid_df))
        return valid_df, []
    except Exception as exc:
        log.warning("Validation errors found: %s", exc)
        # Try row-by-row to collect errors
        valid_rows, error_rows = [], []
        for idx, row in df.iterrows():
            try:
                schema.validate(pd.DataFrame([row]))
                valid_rows.append(row)
            except Exception as row_exc:
                errors.append({"row": idx, "error": str(row_exc)[:120]})
                error_rows.append(row)

        valid_df = pd.DataFrame(valid_rows)
        log.info("Validation: %d valid, %d rejected", len(valid_df), len(error_rows))
        return valid_df, errors


def _manual_validate(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Fallback manual validation without pandera."""
    errors = []
    mask = pd.Series([True] * len(df))

    if "id" in df.columns:
        bad = df["id"].isna() | (pd.to_numeric(df["id"], errors="coerce") <= 0)
        errors += [{"row": i, "error": "invalid id"} for i in df[bad].index]
        mask &= ~bad

    if "age" in df.columns:
        age_num = pd.to_numeric(df["age"], errors="coerce")
        bad = (age_num < 0) | (age_num > 120)
        errors += [{"row": i, "error": "age out of range"} for i in df[bad.fillna(False)].index]
        mask &= ~bad.fillna(False)

    return df[mask].copy(), errors
