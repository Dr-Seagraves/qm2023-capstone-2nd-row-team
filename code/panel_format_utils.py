"""Utilities for reading the final panel in either wide or tidy-long form."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


LONG_COLUMNS = {"date", "variable", "value"}


def is_long_panel(df: pd.DataFrame) -> bool:
    """Return True when the DataFrame matches the tidy-long panel schema."""
    return LONG_COLUMNS.issubset(df.columns)


def long_to_wide(df_long: pd.DataFrame) -> pd.DataFrame:
    """Convert tidy-long panel data to the analysis wide format."""
    wide = (
        df_long.pivot_table(
            index="date",
            columns="variable",
            values="value",
            aggfunc="first",
        )
        .reset_index()
        .rename_axis(columns=None)
    )
    return wide


def ensure_wide_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize panel data to wide format expected by analysis scripts."""
    if is_long_panel(df):
        return long_to_wide(df)
    return df.copy()


def load_panel_as_wide(path: str | Path) -> pd.DataFrame:
    """Load panel CSV and always return a wide DataFrame with parsed dates."""
    df = pd.read_csv(path)
    if "date" not in df.columns:
        raise ValueError("Panel file must include a 'date' column.")

    df["date"] = pd.to_datetime(df["date"])
    df = ensure_wide_panel(df)
    df = df.sort_values("date").reset_index(drop=True)
    return df
