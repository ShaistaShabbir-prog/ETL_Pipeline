# dbt Transformation Layer

## Setup
```bash
pip install dbt-postgres
dbt init etl_project
```

## Models

### staging/stg_source.sql
```sql
-- Clean and standardise raw source data
SELECT
  id::INTEGER                            AS id,
  TRIM(LOWER(email))                     AS email,
  NULLIF(age, '')::INTEGER               AS age,
  TO_DATE(date_col, 'YYYY-MM-DD')        AS event_date,
  CURRENT_TIMESTAMP                      AS loaded_at
FROM {{ source('raw', 'source_table') }}
WHERE id IS NOT NULL
```

### marts/final_table.sql
```sql
-- Business-level aggregation
SELECT
  email,
  COUNT(*)          AS event_count,
  AVG(age)          AS avg_age,
  MIN(event_date)   AS first_seen,
  MAX(event_date)   AS last_seen
FROM {{ ref('stg_source') }}
GROUP BY email
```

## Tests (dbt test)
```yaml
# models/schema.yml
models:
  - name: stg_source
    columns:
      - name: id
        tests: [not_null, unique]
      - name: email
        tests: [not_null]
```

## Run
```bash
dbt run      # execute all models
dbt test     # run data tests
dbt docs generate && dbt docs serve  # lineage docs
```
