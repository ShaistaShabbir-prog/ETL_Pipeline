"""
etl_pipeline/data_quality/expectations_suite.py

Great Expectations data quality suite for the ETL pipeline.
Runs before the LOAD step — fails the pipeline if expectations are violated.

Usage:
    python etl_pipeline/data_quality/expectations_suite.py --csv data/input.csv
"""
import great_expectations as gx
import pandas as pd
import sys
import argparse


def build_suite(df: pd.DataFrame) -> dict:
    """
    Define and run data quality expectations on a DataFrame.
    Returns a dict with success flag and failed expectations.
    """
    context = gx.get_context(mode="ephemeral")
    ds = context.sources.add_pandas("pipeline_source")
    da = ds.add_dataframe_asset("batch")
    batch = da.build_batch_request(dataframe=df)
    validator = context.get_validator(batch_request=batch)

    # ── Schema expectations ──────────────────────────────────
    validator.expect_table_columns_to_match_ordered_list(
        column_list=list(df.columns)
    )
    validator.expect_table_row_count_to_be_between(min_value=1, max_value=10_000_000)

    # ── Null checks (all columns should have < 5% nulls) ────
    for col in df.columns:
        validator.expect_column_values_to_not_be_null(
            column=col, mostly=0.95
        )

    # ── Type and range checks (customize per your schema) ───
    for col in df.select_dtypes(include=["number"]).columns:
        validator.expect_column_values_to_be_of_type(column=col, type_="NUMBER")

    for col in df.select_dtypes(include=["object"]).columns:
        validator.expect_column_values_to_not_match_regex(
            column=col, regex=r"^\s*$", mostly=0.99
        )

    # ── Uniqueness check on first column (assumed primary key) ──
    if len(df.columns) > 0:
        validator.expect_column_values_to_be_unique(column=df.columns[0], mostly=0.99)

    result = validator.validate()
    failed = [r for r in result.results if not r.success]

    return {
        "success": result.success,
        "total_expectations": len(result.results),
        "failed_count": len(failed),
        "failed_expectations": [str(f.expectation_config.expectation_type) for f in failed],
        "statistics": result.statistics,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to input CSV")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    print(f"Validating {len(df):,} rows × {len(df.columns)} columns...")
    report = build_suite(df)

    print(f"\n{'='*50}")
    print(f"DATA QUALITY REPORT")
    print(f"{'='*50}")
    print(f"Overall: {'✅ PASSED' if report['success'] else '❌ FAILED'}")
    print(f"Expectations run: {report['total_expectations']}")
    print(f"Failed:           {report['failed_count']}")

    if report["failed_expectations"]:
        print("\nFailed checks:")
        for f in report["failed_expectations"]:
            print(f"  ❌ {f}")

    if not report["success"]:
        print("\n⛔ Pipeline halted — fix data quality issues before loading.")
        sys.exit(1)

    print("\n✅ All quality checks passed — safe to load.")


if __name__ == "__main__":
    main()
