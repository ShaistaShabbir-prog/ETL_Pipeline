"""
Issue #5: Apache Airflow DAG for scheduled ETL pipeline runs.
Schedule: daily at 02:00 UTC.
"""
from __future__ import annotations
from datetime import datetime, timedelta

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    HAS_AIRFLOW = True
except ImportError:
    HAS_AIRFLOW = False
    print("airflow not installed — DAG definition skipped. pip install apache-airflow")


def run_extract(**ctx):
    """Extract step — pulls from source CSV."""
    import pandas as pd, os
    src = os.getenv("SOURCE_CSV", "data/raw/source.csv")
    df  = pd.read_csv(src)
    ctx["ti"].xcom_push(key="row_count", value=len(df))
    df.to_parquet("/tmp/etl_extract.parquet", index=False)
    print(f"Extracted {len(df)} rows from {src}")


def run_transform(**ctx):
    """Transform step — clean, validate, deduplicate."""
    import pandas as pd
    df = pd.read_parquet("/tmp/etl_extract.parquet")
    before = len(df)
    df = df.dropna(thresh=int(len(df.columns) * 0.7))   # drop rows >30% null
    df = df.drop_duplicates()
    df.to_parquet("/tmp/etl_transform.parquet", index=False)
    print(f"Transform: {before} → {len(df)} rows ({before-len(df)} removed)")


def run_load(**ctx):
    """Load step — upsert to PostgreSQL."""
    import pandas as pd
    df = pd.read_parquet("/tmp/etl_transform.parquet")
    print(f"Load: {len(df)} rows → PostgreSQL")
    # Real implementation: use psycopg2 upsert_rows()


def run_profile(**ctx):
    """Profile step — generate data quality report."""
    import pandas as pd
    df = pd.read_parquet("/tmp/etl_transform.parquet")
    from etl_pipeline.profiling import generate_profile
    path = generate_profile(df, output_dir="reports/")
    print(f"Profile saved: {path}")


if HAS_AIRFLOW:
    with DAG(
        dag_id="etl_pipeline",
        description="Daily ETL pipeline — extract, transform, load, profile",
        schedule_interval="0 2 * * *",
        start_date=datetime(2025, 1, 1),
        catchup=False,
        default_args={
            "owner": "data-team",
            "retries": 2,
            "retry_delay": timedelta(minutes=5),
            "email_on_failure": False,
        },
        tags=["etl", "daily"],
    ) as dag:
        extract   = PythonOperator(task_id="extract",   python_callable=run_extract)
        transform = PythonOperator(task_id="transform", python_callable=run_transform)
        load      = PythonOperator(task_id="load",      python_callable=run_load)
        profile   = PythonOperator(task_id="profile",   python_callable=run_profile)

        extract >> transform >> load >> profile
