"""
Issue #3: Incremental loading — only extract records modified since last run.
Tracks last_run_timestamp in etl_metadata table.
"""
import logging
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger(__name__)


def get_last_run(conn) -> str | None:
    """Return ISO timestamp of last successful ETL run, or None."""
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS etl_metadata (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        cur.execute("SELECT value FROM etl_metadata WHERE key = 'last_run'")
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        log.warning("get_last_run failed: %s", e)
        return None


def set_last_run(conn, ts: str | None = None) -> None:
    """Update last_run timestamp after successful ETL run."""
    ts = ts or datetime.now(timezone.utc).isoformat()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO etl_metadata (key, value, updated_at)
            VALUES ('last_run', %s, NOW())
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
        """, (ts,))
        conn.commit()
        log.info("Updated last_run to %s", ts)
    except Exception as e:
        log.warning("set_last_run failed: %s", e)


def extract_incremental(conn, table: str, updated_col: str = "updated_at",
                         limit: int = 10_000) -> list[dict[str, Any]]:
    """
    Extract only rows updated since last ETL run.
    Falls back to full extract if no last_run timestamp exists.
    """
    last_run = get_last_run(conn)
    try:
        cur = conn.cursor()
        if last_run:
            log.info("Incremental extract from %s since %s", table, last_run)
            cur.execute(f"""
                SELECT * FROM {table}
                WHERE {updated_col} > %s
                ORDER BY {updated_col}
                LIMIT %s
            """, (last_run, limit))
        else:
            log.info("Full extract from %s (no previous run)", table)
            cur.execute(f"SELECT * FROM {table} ORDER BY {updated_col} LIMIT %s", (limit,))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        log.info("Extracted %d rows", len(rows))
        return rows
    except Exception as e:
        log.error("Incremental extract failed: %s", e)
        return []


def upsert_rows(conn, table: str, rows: list[dict], pk: str = "id") -> int:
    """
    Upsert rows — INSERT ... ON CONFLICT DO UPDATE.
    Returns number of rows upserted.
    """
    if not rows: return 0
    cols    = list(rows[0].keys())
    updates = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c != pk)
    placeholders = ", ".join(["%s"] * len(cols))
    col_str = ", ".join(cols)
    sql = f"""
        INSERT INTO {table} ({col_str})
        VALUES ({placeholders})
        ON CONFLICT ({pk}) DO UPDATE SET {updates}
    """
    try:
        cur = conn.cursor()
        cur.executemany(sql, [tuple(r[c] for c in cols) for r in rows])
        conn.commit()
        log.info("Upserted %d rows into %s", len(rows), table)
        return len(rows)
    except Exception as e:
        log.error("Upsert failed: %s", e)
        conn.rollback()
        return 0
