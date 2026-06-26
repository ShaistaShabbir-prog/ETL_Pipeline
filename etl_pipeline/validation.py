"""
Issue #10: Pandera schema validation before load step.
"""
from __future__ import annotations
import logging
import pandas as pd
log = logging.getLogger(__name__)


def validate(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Validate DataFrame against expected schema.
    Returns (clean_df, list_of_errors).
    Falls back gracefully if pandera not installed.
    """
    errors = []
    try:
        import pandera as pa

        schema = pa.DataFrameSchema({
            "id":    pa.Column(int, nullable=False,
                               checks=pa.Check.ge(0), coerce=True),
            "email": pa.Column(str, nullable=True,
                               checks=pa.Check.str_matches(r".+@.+\..+", error="invalid email")),
            "age":   pa.Column(float, nullable=True,
                               checks=[pa.Check.ge(0), pa.Check.le(130)], coerce=True),
        }, drop_invalid_rows=True)

        try:
            clean = schema.validate(df, lazy=True)
            return clean, []
        except pa.errors.SchemaErrors as exc:
            for _, row in exc.failure_cases.iterrows():
                errors.append(f"Col={row.column} check={row.check} value={row.failure_case}")
            # Return valid rows only
            valid_idx = df.index.difference(exc.failure_cases.index.unique())
            return df.loc[valid_idx], errors

    except ImportError:
        log.warning("pandera not installed — skipping validation. pip install pandera")
        # Basic null / duplicate check
        before = len(df)
        df = df.dropna(how="all").drop_duplicates()
        if len(df) < before:
            errors.append(f"Dropped {before-len(df)} null/duplicate rows")
        return df, errors
