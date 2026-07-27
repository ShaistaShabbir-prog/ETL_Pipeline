"""
etl_pipeline/extract.py

Data extraction module — reads from CSV files or REST APIs.

Usage:
    from etl_pipeline.extract import extract_from_csv, extract_from_api
    df = extract_from_csv("data/sample_events.csv")
"""
from __future__ import annotations
import logging
from pathlib import Path
import pandas as pd
import requests

logger = logging.getLogger(__name__)


def extract_from_csv(path: str | Path, **read_kwargs) -> pd.DataFrame:
    """
    Extract data from a local CSV file.

    Args:
        path: Path to CSV file
        **read_kwargs: Additional kwargs passed to pd.read_csv

    Returns:
        DataFrame with raw data

    Raises:
        FileNotFoundError: If path does not exist
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    df = pd.read_csv(path, **read_kwargs)
    logger.info(f"Extracted {len(df):,} rows from {path}")
    return df


def extract_from_api(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int = 30,
) -> list[dict]:
    """
    Extract data from a REST API endpoint.

    Args:
        url: API endpoint URL
        params: Query parameters
        headers: HTTP headers (e.g. Authorization)
        timeout: Request timeout in seconds

    Returns:
        List of records from the API
    """
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        # Handle both list and dict responses
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            # Common patterns: {"data": [...]} or {"results": [...]} or {"items": [...]}
            for key in ("data", "results", "items", "records", "events"):
                if key in data and isinstance(data[key], list):
                    records = data[key]
                    break
            else:
                records = [data]
        else:
            records = []

        logger.info(f"Extracted {len(records):,} records from {url}")
        return records

    except requests.RequestException as e:
        logger.error(f"API extraction failed: {e}")
        raise


def extract_from_gdacs(limit: int = 50) -> pd.DataFrame:
    """
    Extract live disaster events from GDACS RSS feed.
    Returns a DataFrame ready for the ETL pipeline.
    """
    try:
        import feedparser
        feed = feedparser.parse("https://www.gdacs.org/xml/rss.xml")
        records = []
        for entry in feed.entries[:limit]:
            records.append({
                "id":          entry.get("id", ""),
                "event_type":  entry.get("gdacs_eventtype", "XX"),
                "location":    entry.get("gdacs_country", "Unknown"),
                "event_date":  entry.get("published", ""),
                "description": entry.get("summary", "")[:300],
            })
        df = pd.DataFrame(records)
        logger.info(f"Extracted {len(df)} events from GDACS")
        return df
    except Exception as e:
        logger.warning(f"GDACS extraction failed: {e} — returning empty DataFrame")
        return pd.DataFrame(columns=["id","event_type","location","event_date","description"])
