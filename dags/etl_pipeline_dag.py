"""
dags/etl_pipeline_dag.py

Apache Airflow DAG for the ETL pipeline.
Orchestrates: Extract → Validate → Transform → Load → Notify

Setup:
  1. pip install apache-airflow
  2. export AIRFLOW_HOME=./airflow
  3. airflow db init
  4. airflow scheduler &
  5. airflow webserver -p 8080
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.trigger_rule import TriggerRule
import logging

logger = logging.getLogger(__name__)

# ── Default args ─────────────────────────────────────────────
default_args = {
    "owner": "shaista",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
}

# ── Task functions ────────────────────────────────────────────
def extract(**context):
    """Extract data from source (CSV / API / DB)."""
    from etl_pipeline.extract import run_extraction
    logger.info("Starting extraction...")
    result = run_extraction()
    context["ti"].xcom_push(key="row_count", value=result["rows"])
    logger.info(f"Extracted {result['rows']:,} rows")
    return result["output_path"]


def validate(**context):
    """Run Great Expectations data quality suite."""
    import subprocess, sys
    csv_path = context["ti"].xcom_pull(task_ids="extract")
    result = subprocess.run(
        [sys.executable, "etl_pipeline/data_quality/expectations_suite.py", "--csv", csv_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise ValueError(f"Data quality validation failed:\n{result.stdout}\n{result.stderr}")
    logger.info("Data quality: PASSED")
    return csv_path


def transform(**context):
    """Clean, normalize, and enrich the data."""
    from etl_pipeline.transform import run_transformation
    csv_path = context["ti"].xcom_pull(task_ids="validate")
    logger.info("Starting transformation...")
    output = run_transformation(csv_path)
    logger.info(f"Transformed → {output}")
    return output


def load(**context):
    """Load validated, transformed data into PostgreSQL."""
    from etl_pipeline.load import run_load
    transformed_path = context["ti"].xcom_pull(task_ids="transform")
    logger.info("Starting load...")
    rows_loaded = run_load(transformed_path)
    logger.info(f"Loaded {rows_loaded:,} rows into database")
    return rows_loaded


def on_failure_callback(context):
    logger.error(f"Task {context['task_instance_key_str']} FAILED: {context['exception']}")


# ── DAG definition ────────────────────────────────────────────
with DAG(
    dag_id="etl_pipeline",
    default_args=default_args,
    description="ETL pipeline: Extract → Validate (GX) → Transform → Load",
    schedule_interval="0 6 * * *",   # daily at 06:00 UTC
    catchup=False,
    tags=["etl", "data-quality", "production"],
) as dag:

    t_extract = PythonOperator(
        task_id="extract",
        python_callable=extract,
        on_failure_callback=on_failure_callback,
    )

    t_validate = PythonOperator(
        task_id="validate",
        python_callable=validate,
        on_failure_callback=on_failure_callback,
    )

    t_transform = PythonOperator(
        task_id="transform",
        python_callable=transform,
        on_failure_callback=on_failure_callback,
    )

    t_load = PythonOperator(
        task_id="load",
        python_callable=load,
        on_failure_callback=on_failure_callback,
    )

    t_notify_success = EmailOperator(
        task_id="notify_success",
        to="shaista.s.shabbir@gmail.com",
        subject="✅ ETL Pipeline Completed",
        html_content="""<h2>ETL Pipeline Success</h2>
        <p>Date: {{ ds }}<br>
        Rows extracted: {{ ti.xcom_pull(task_ids=\'extract\', key=\'row_count\') }}</p>""",
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    # Pipeline order
    t_extract >> t_validate >> t_transform >> t_load >> t_notify_success
