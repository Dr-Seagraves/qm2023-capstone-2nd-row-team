"""Prepare canonical time-series and event-study datasets for analysis.

Outputs:
- data/final/analysis_time_series_ready.csv
- data/final/analysis_event_study_ready.csv
- results/reports/time_series_data_readiness.md

Purpose:
- Identify the correct dataset for aggregate time-series analysis.
- Validate date continuity, uniqueness, sorting, and missingness.
- Export a time-series-ready file with lagged regressors used in the M3 models.
- Export an event-study-ready file with event timing variables for major shocks.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config_paths import FINAL_DATA_DIR, REPORTS_DIR
from panel_format_utils import load_panel_as_wide


SOURCE_PATH = FINAL_DATA_DIR / "analysis_panel_wide.csv"
TS_OUTPUT_PATH = FINAL_DATA_DIR / "analysis_time_series_ready.csv"
EVENT_OUTPUT_PATH = FINAL_DATA_DIR / "analysis_event_study_ready.csv"
REPORT_PATH = REPORTS_DIR / "time_series_data_readiness.md"

EXPECTED_START = pd.Timestamp("2004-01-31")
EXPECTED_END = pd.Timestamp("2024-12-31")
GFC_DATE = pd.Timestamp("2008-09-30")
COVID_DATE = pd.Timestamp("2020-03-31")


def validate_wide_time_series(df: pd.DataFrame) -> list[str]:
    """Run structural checks for the canonical monthly time-series dataset."""
    issues: list[str] = []

    if df["date"].duplicated().any():
        issues.append("Duplicate monthly dates found.")

    if not df["date"].is_monotonic_increasing:
        issues.append("Dates are not sorted ascending.")

    expected_dates = pd.date_range(start=EXPECTED_START, end=EXPECTED_END, freq="ME")
    actual_dates = pd.DatetimeIndex(df["date"])
    missing_dates = expected_dates.difference(actual_dates)
    extra_dates = actual_dates.difference(expected_dates)

    if len(missing_dates) > 0:
        issues.append(f"Missing monthly dates: {len(missing_dates)}")
    if len(extra_dates) > 0:
        issues.append(f"Unexpected dates outside target range: {len(extra_dates)}")

    if df.isna().sum().sum() > 0:
        issues.append(f"Missing values present: {int(df.isna().sum().sum())}")

    if df["date"].min() != EXPECTED_START:
        issues.append(f"Start date mismatch: found {df['date'].min().date()}")
    if df["date"].max() != EXPECTED_END:
        issues.append(f"End date mismatch: found {df['date'].max().date()}")

    return issues


def build_time_series_ready(df: pd.DataFrame) -> pd.DataFrame:
    """Create the canonical monthly time-series dataset used for regressions."""
    out = df.copy().sort_values("date").reset_index(drop=True)
    out["year"] = out["date"].dt.year
    out["month"] = out["date"].dt.month
    out["t_index"] = range(len(out))

    lag_map = {
        "sentiment_michigan_ics": "sentiment_michigan_ics_l1",
        "bull_bear_spread": "bull_bear_spread_l1",
        "smb": "smb_l1",
        "hml": "hml_l1",
        "rmw": "rmw_l1",
        "cma": "cma_l1",
    }
    for source, target in lag_map.items():
        out[target] = out[source].shift(1)

    return out


def add_event_study_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Add event-study timing columns for the main macro shocks."""
    out = df.copy()
    out["post_gfc"] = (out["date"] >= GFC_DATE).astype(int)
    out["post_covid"] = (out["date"] >= COVID_DATE).astype(int)

    out["event_time_gfc"] = (
        (out["date"].dt.year - GFC_DATE.year) * 12
        + (out["date"].dt.month - GFC_DATE.month)
    )
    out["event_time_covid"] = (
        (out["date"].dt.year - COVID_DATE.year) * 12
        + (out["date"].dt.month - COVID_DATE.month)
    )

    for window in [6, 12, 24]:
        out[f"gfc_window_pm{window}"] = out["event_time_gfc"].between(-window, window).astype(int)
        out[f"covid_window_pm{window}"] = out["event_time_covid"].between(-window, window).astype(int)

    return out


def write_report(source_df: pd.DataFrame, ts_df: pd.DataFrame, event_df: pd.DataFrame, issues: list[str]) -> None:
    """Write a short report identifying the correct time-series dataset."""
    if issues:
        status_line = "Status: issues found. Review checks before analysis."
        check_lines = "\n".join(f"- {issue}" for issue in issues)
    else:
        status_line = "Status: validated and ready for aggregate time-series analysis."
        check_lines = "- No duplicate dates\n- No missing months\n- No missing values\n- Correct monthly coverage from 2004-01 to 2024-12"

    report = f"""# Time-Series Dataset Readiness

## Correct Dataset Choice

The correct dataset for the project's aggregate time-series analysis is:

- `{SOURCE_PATH}`

Why this is the correct version:

- It has **one row per month**.
- It has **one column per variable**.
- It matches the structure used for market-return regressions where `mkt_ret` is the outcome and sentiment/factor series are regressors.
- It is the wide companion file written by the merge pipeline, while `analysis_panel.csv` is the reshaped long file used for stacked FE/DiD analysis.

## Validation Checks

{status_line}

{check_lines}

## Dataset Shapes

- Source wide monthly dataset: **{len(source_df)} rows x {len(source_df.columns)} columns**
- Time-series-ready dataset: **{len(ts_df)} rows x {len(ts_df.columns)} columns**
- Event-study-ready dataset: **{len(event_df)} rows x {len(event_df.columns)} columns**

## Recommended Use

- Use `{TS_OUTPUT_PATH}` for ARDL / distributed-lag / predictive time-series regressions.
- Use `{EVENT_OUTPUT_PATH}` for event-window summaries and simple event-study style plots around 2008-09 and 2020-03.
- Keep `analysis_panel.csv` for the stacked long FE and DiD specifications.

## Notes

- This project is fundamentally an **aggregate monthly time-series dataset**.
- The panel models are created by reshaping that same monthly dataset into long form, so they are not based on firm-level cross sections.
"""

    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    source_df = load_panel_as_wide(SOURCE_PATH)
    issues = validate_wide_time_series(source_df)

    ts_df = build_time_series_ready(source_df)
    event_df = add_event_study_fields(ts_df)

    ts_df.to_csv(TS_OUTPUT_PATH, index=False)
    event_df.to_csv(EVENT_OUTPUT_PATH, index=False)
    write_report(source_df=source_df, ts_df=ts_df, event_df=event_df, issues=issues)

    print(f"Source dataset: {SOURCE_PATH}")
    print(f"Time-series-ready dataset: {TS_OUTPUT_PATH}")
    print(f"Event-study-ready dataset: {EVENT_OUTPUT_PATH}")
    print(f"Readiness report: {REPORT_PATH}")
    if issues:
        print("Validation issues detected:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("Validation passed with no issues.")


if __name__ == "__main__":
    main()