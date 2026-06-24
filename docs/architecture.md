# ETL Pipeline — Architecture & Sample Output

## Architecture

```
CSV Source
    │
    ▼
┌─────────────┐
│   EXTRACT   │  Read CSV, validate schema
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  TRANSFORM  │  Clean nulls, standardise dates,
│             │  validate ranges, deduplicate
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    LOAD     │  Upsert to PostgreSQL
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   REPORT    │  Data quality metrics logged
└─────────────┘
```

## Sample input (raw CSV)

| id | name | age | email | date |
|---|---|---|---|---|
| 1 | Alice | 28 | alice@example.com | 2024-01-15 |
| 2 | Bob | -5 | invalid-email | 2024/01/16 |
| 3 | NULL | 30 | carol@example.com | 2024-01-17 |
| 1 | Alice | 28 | alice@example.com | 2024-01-15 |

## Sample output (after transform)

| id | name | age | email | date | quality_flag |
|---|---|---|---|---|---|
| 1 | Alice | 28 | alice@example.com | 2024-01-15 | PASS |
| 3 | Carol | 30 | carol@example.com | 2024-01-17 | PASS |

Rows rejected: 2 (invalid age, duplicate)

## Data quality metrics

```
Total rows:      100
Rows passed:      87  (87%)
Rows rejected:    13  (13%)
  - Null values:   5
  - Invalid email: 4
  - Out of range:  3
  - Duplicates:    1
```

## Running tests

```bash
cd etl_pipeline
pip install -r requirements.txt
pytest tests/ -v
```
