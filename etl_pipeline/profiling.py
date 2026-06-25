"""
Issue #4: Data profiling report after each ETL run.
Generates HTML report using ydata-profiling (formerly pandas-profiling).
Falls back to plain-text summary if ydata-profiling not installed.
"""
from __future__ import annotations
import logging
import os
from datetime import datetime
from typing import Any

log = logging.getLogger(__name__)


def generate_profile(df, output_dir: str = "reports/") -> str:
    """
    Generate HTML data quality report.
    Requires: pip install ydata-profiling
    Falls back to plain text summary if not available.
    """
    os.makedirs(output_dir, exist_ok=True)
    date_str  = datetime.now().strftime("%Y-%m-%d")
    html_path = os.path.join(output_dir, f"profile_{date_str}.html")
    txt_path  = os.path.join(output_dir, f"profile_{date_str}.txt")

    try:
        from ydata_profiling import ProfileReport
        profile = ProfileReport(df, title=f"ETL Run — {date_str}",
                                minimal=True, explorative=False)
        profile.to_file(html_path)
        log.info("Profile saved to %s", html_path)
        return html_path
    except ImportError:
        log.warning("ydata-profiling not installed — generating text summary")
        return _text_summary(df, txt_path, date_str)


def _text_summary(df, path: str, date_str: str) -> str:
    rows, cols = df.shape
    null_pct   = (df.isnull().sum() / rows * 100).to_dict()
    dup_count  = df.duplicated().sum()
    summary    = [
        f"ETL Data Quality Report — {date_str}",
        f"{'='*50}",
        f"Rows:       {rows:,}",
        f"Columns:    {cols}",
        f"Duplicates: {dup_count:,}  ({dup_count/rows*100:.1f}%)",
        "",
        "Null percentages per column:",
    ]
    for col, pct in sorted(null_pct.items(), key=lambda x: -x[1]):
        flag = " ⚠️" if pct > 10 else ""
        summary.append(f"  {col:30} {pct:5.1f}%{flag}")
    summary.extend([
        "",
        "Data types:",
        *[f"  {col:30} {str(dtype)}" for col, dtype in df.dtypes.items()],
    ])
    with open(path, "w") as f:
        f.write("
".join(summary))
    log.info("Text profile saved to %s", path)
    return path
