# dbt Transformation Layer

Issue #11: SQL-based transformations with lineage tracking.

## Setup

```bash
pip install dbt-core dbt-postgres
dbt init etl_project
```

## Project structure

```
dbt_project/
  models/
    staging/
      stg_source.sql        ← raw → cleaned
    marts/
      final_table.sql       ← business logic
  tests/
    not_null.yml            ← column-level tests
    unique.yml              ← uniqueness checks
  dbt_project.yml           ← project config
```

## Run

```bash
cd dbt_project
dbt run          # execute transformations
dbt test         # run data quality tests
dbt docs generate && dbt docs serve   # view lineage
```

## Example staging model

```sql
-- models/staging/stg_source.sql
SELECT
  CAST(id AS INTEGER)           AS id,
  LOWER(TRIM(email))            AS email,
  CAST(age AS FLOAT)            AS age,
  CAST(date AS DATE)            AS date,
  CURRENT_TIMESTAMP             AS loaded_at
FROM {{ source('raw', 'source_table') }}
WHERE id IS NOT NULL
  AND age BETWEEN 0 AND 120
```

## Tests (tests/not_null.yml)

```yaml
version: 2
models:
  - name: stg_source
    columns:
      - name: id
        tests: [not_null, unique]
      - name: email
        tests: [not_null]
```
