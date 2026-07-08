-- dbt_project/models/staging/stg_events.sql
-- Staging model: clean and normalize raw event data
-- Source: raw events table from extraction step

{{ config(materialized='view') }}

SELECT
    CAST(id AS VARCHAR)                                    AS event_id,
    TRIM(LOWER(event_type))                                AS event_type,
    TRIM(location)                                         AS location,
    CAST(event_date AS DATE)                               AS event_date,
    TRIM(description)                                      AS description,
    CURRENT_TIMESTAMP                                      AS _loaded_at,
    '{{ run_started_at }}'                                 AS _dbt_run_at

FROM {{ source('raw', 'events') }}

-- Filter out clearly invalid records
WHERE id IS NOT NULL
  AND event_date IS NOT NULL
  AND event_type IS NOT NULL
