-- dbt_project/models/marts/mart_event_summary.sql
-- Business mart: aggregated event statistics per type per month
-- Used by: dashboards, reporting, downstream ML features

{{ config(materialized='table') }}

WITH base AS (
    SELECT * FROM {{ ref('stg_events') }}
),

monthly_agg AS (
    SELECT
        event_type,
        DATE_TRUNC('month', event_date)                    AS month,
        COUNT(*)                                           AS event_count,
        COUNT(DISTINCT location)                           AS unique_locations,
        MIN(event_date)                                    AS first_event,
        MAX(event_date)                                    AS last_event
    FROM base
    GROUP BY 1, 2
)

SELECT
    event_type,
    month,
    event_count,
    unique_locations,
    first_event,
    last_event,
    SUM(event_count) OVER (
        PARTITION BY event_type
        ORDER BY month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                                      AS cumulative_count
FROM monthly_agg
ORDER BY month DESC, event_count DESC
