# ETL Pipeline

A production-quality ETL pipeline with **data quality validation** (Great Expectations), **orchestration** (Apache Airflow), and **transformation** (dbt).

[![CI](https://github.com/ShaistaShabbir-prog/ETL_Pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/ShaistaShabbir-prog/ETL_Pipeline/actions)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Apache Airflow DAG                    │
│                                                          │
│  [Extract] → [Validate (GX)] → [Transform (dbt)] → [Load] → [Notify]
│     ↓              ↓                 ↓               ↓
│   CSV/API    GX Expectations     SQL models      PostgreSQL
│   sources    (schema, nulls,     (staging +      (or any DB)
│              uniqueness)          marts)                     │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Orchestration | Apache Airflow | DAG scheduling, retries, monitoring |
| Data Quality | Great Expectations | Schema, null, range, uniqueness checks |
| Transformation | dbt | SQL models, tests, data lineage |
| Storage | PostgreSQL | Output data warehouse |
| Language | Python 3.11 | Extract + load scripts |

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/ShaistaShabbir-prog/ETL_Pipeline.git
cd ETL_Pipeline
pip install -r requirements.txt

# 2. Run data quality check on sample data
python etl_pipeline/data_quality/expectations_suite.py --csv data/sample_events.csv

# 3. Run Airflow locally (optional)
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init
airflow scheduler &
airflow webserver -p 8080 &
# Open http://localhost:8080 — trigger dag 'etl_pipeline'

# 4. Run dbt models (requires PostgreSQL)
cd dbt_project
dbt run
dbt test
```

---

## Project Structure

```
ETL_Pipeline/
├── dags/
│   └── etl_pipeline_dag.py     ← Airflow DAG (Extract→Validate→Transform→Load)
├── data/
│   └── sample_events.csv       ← Sample input data for testing
├── dbt_project/
│   ├── models/
│   │   ├── staging/stg_events.sql    ← Clean + normalize raw data
│   │   └── marts/mart_event_summary.sql ← Business aggregations
│   └── schema.yml              ← dbt source + model tests
├── etl_pipeline/
│   ├── data_quality/
│   │   └── expectations_suite.py  ← Great Expectations validation
│   ├── extract.py              ← Data extraction (CSV/API)
│   ├── transform.py            ← Business logic transformations
│   └── load.py                 ← Database loading
└── requirements.txt
```

---

## Data Quality Checks (Great Expectations)

The pipeline validates data **before loading** using these checks:

| Check | What it validates |
|---|---|
| Schema | Column names match expected schema |
| Not null | All required columns have values (95%+ non-null) |
| Uniqueness | Primary key column has no duplicates |
| Type check | Numeric columns contain numbers |
| String check | Text columns are not blank/whitespace |

```bash
# Run manually
python etl_pipeline/data_quality/expectations_suite.py --csv your_data.csv
```

---

## Airflow DAG

The DAG runs daily at 06:00 UTC with 3 retries (exponential backoff):

```
extract → validate (GX) → transform → load → notify_success
```

Each task logs to Airflow's UI with full error context.

---

## dbt Models

| Model | Type | Description |
|---|---|---|
| `stg_events` | View | Clean + normalize raw events (type cast, trim, filter nulls) |
| `mart_event_summary` | Table | Monthly aggregation by event type + cumulative counts |

Run tests: `dbt test` — checks uniqueness and not-null on all key columns.

---

## Research Context

This pipeline was built as part of the **A.L.E.R.T** research project (civil event detection for Hamburg). It processes ~19,444 social media records through extraction, quality validation, and aggregation.

**Related:** [EventDetectionAndEventExtraction](https://github.com/ShaistaShabbir-prog/EventDetectionAndEventExtraction)

---

## Author

**Shaista Shabbir** — Research Associate, TU Dortmund University · Lamarr Institute for ML & AI
