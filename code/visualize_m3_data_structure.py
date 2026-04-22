"""Visualize the data structure used in the M3 regressions.

Outputs:
- results/figures/m3_data_structure_overview.png
- results/reports/m3_data_structure_summary.md

This script clarifies that:
- The market-return regressions use a single monthly time series in wide format.
- The FE and DiD regressions use a stacked long panel where each variable is
  treated as an entity observed over time.
"""

from __future__ import annotations

from textwrap import dedent

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from config_paths import FIGURES_DIR, FINAL_DATA_DIR, REPORTS_DIR
from panel_format_utils import is_long_panel, load_panel_as_wide


PANEL_PATH = FINAL_DATA_DIR / "analysis_panel.csv"
FIGURE_PATH = FIGURES_DIR / "m3_data_structure_overview.png"
REPORT_PATH = REPORTS_DIR / "m3_data_structure_summary.md"


def load_long_panel(path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    if is_long_panel(raw):
        long_df = raw.copy()
    else:
        value_cols = [column for column in raw.columns if column != "date"]
        long_df = raw.melt(id_vars="date", value_vars=value_cols, var_name="variable", value_name="value")

    long_df["date"] = pd.to_datetime(long_df["date"])
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
    long_df = long_df.sort_values(["date", "variable"]).reset_index(drop=True)
    return long_df


def build_market_regression_sample(wide_df: pd.DataFrame) -> pd.DataFrame:
    market_df = wide_df.copy().sort_values("date").reset_index(drop=True)
    market_df["sentiment_michigan_ics_l1"] = market_df["sentiment_michigan_ics"].shift(1)
    market_df["bull_bear_spread_l1"] = market_df["bull_bear_spread"].shift(1)
    market_df["smb_l1"] = market_df["smb"].shift(1)
    market_df["hml_l1"] = market_df["hml"].shift(1)
    market_df["rmw_l1"] = market_df["rmw"].shift(1)
    market_df["cma_l1"] = market_df["cma"].shift(1)

    return market_df.dropna(
        subset=[
            "mkt_ret",
            "sentiment_michigan_ics_l1",
            "bull_bear_spread_l1",
            "smb_l1",
            "hml_l1",
            "rmw_l1",
            "cma_l1",
        ]
    ).copy()


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Render a small DataFrame as markdown without optional dependencies."""
    formatted = df.copy()
    for column in formatted.columns:
        if pd.api.types.is_datetime64_any_dtype(formatted[column]):
            formatted[column] = formatted[column].dt.strftime("%Y-%m-%d")

    headers = [str(column) for column in formatted.columns]
    separator = ["---"] * len(headers)
    rows = [headers, separator]
    rows.extend(formatted.astype(str).values.tolist())

    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def create_structure_figure(wide_df: pd.DataFrame, long_df: pd.DataFrame, market_df: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")

    fig = plt.figure(figsize=(16, 12))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.1, 1], width_ratios=[1.15, 1])

    ax1 = fig.add_subplot(grid[0, 0])
    standardized = wide_df[["date", "sentiment_michigan_ics", "bull_bear_spread", "mkt_ret"]].copy()
    for column in ["sentiment_michigan_ics", "bull_bear_spread", "mkt_ret"]:
        centered = standardized[column] - standardized[column].mean()
        standardized[column] = centered / standardized[column].std()

    ax1.plot(standardized["date"], standardized["sentiment_michigan_ics"], label="Michigan sentiment", linewidth=2)
    ax1.plot(standardized["date"], standardized["bull_bear_spread"], label="AAII bull-bear spread", linewidth=2)
    ax1.plot(standardized["date"], standardized["mkt_ret"], label="Market return", linewidth=2)
    ax1.set_title("Single Monthly Time Series Used in Market Regressions", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Standardized value")
    ax1.xaxis.set_major_locator(mdates.YearLocator(4))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax1.tick_params(axis="x", rotation=45)
    ax1.legend(loc="upper right")

    ax2 = fig.add_subplot(grid[0, 1])
    availability = (
        long_df.assign(observed=long_df["value"].notna().astype(int))
        .pivot_table(index="variable", columns="date", values="observed", aggfunc="max")
        .sort_index()
    )
    sns.heatmap(availability, cmap="Blues", cbar=False, ax=ax2)
    ax2.set_title("Stacked Long Panel Used in FE and DiD Models", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Variable treated as entity")
    ax2.set_xticks([])

    ax3 = fig.add_subplot(grid[1, 0])
    shape_df = pd.DataFrame(
        {
            "dataset": [
                "Wide monthly dataset",
                "Market regression sample",
                "Long stacked panel",
                "Panel FE / DiD sample",
            ],
            "rows": [
                len(wide_df),
                len(market_df),
                len(long_df),
                len(long_df.dropna(subset=["value"])),
            ],
        }
    )
    sns.barplot(data=shape_df, x="rows", y="dataset", hue="dataset", palette="crest", dodge=False, legend=False, ax=ax3)
    ax3.set_title("How Many Rows Each Analysis Uses", fontsize=13, fontweight="bold")
    ax3.set_xlabel("Number of rows")
    ax3.set_ylabel("")
    for index, value in enumerate(shape_df["rows"]):
        ax3.text(value + max(shape_df["rows"]) * 0.01, index, f"{value:,}", va="center")

    ax4 = fig.add_subplot(grid[1, 1])
    ax4.axis("off")
    explanation = dedent(
        f"""
        What are these regressions using?

        1. Market regressions:
           One aggregate monthly time series.
           Shape: {len(wide_df)} months x {len(wide_df.columns) - 1} variables.

        2. FE / DiD regressions:
           A stacked long panel built by reshaping the same data.
           Shape: {len(long_df):,} rows = {long_df['variable'].nunique()} variables x {wide_df['date'].nunique()} months.

        Bottom line:
        - For return prediction, this is a time-series design.
        - For FE and DiD, it becomes a synthetic panel.
        - It is not a traditional firm-level panel with many stocks.
        """
    ).strip()
    ax4.text(0, 1, explanation, va="top", ha="left", fontsize=11)

    fig.suptitle("M3 Regression Data Structure", fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURE_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_summary_report(wide_df: pd.DataFrame, long_df: pd.DataFrame, market_df: pd.DataFrame) -> None:
    wide_preview = dataframe_to_markdown(wide_df.head(5))
    long_preview = dataframe_to_markdown(long_df.head(8))

    report = f"""# M3 Data Structure Summary

## Short Answer

The dataset is used in two different ways:

- The market-return regressions are **time-series regressions** on one monthly market series with lagged sentiment and factor controls.
- The fixed-effects and difference-in-differences regressions are run on a **stacked long panel** where each variable is treated as an entity observed each month.

This means the project does **not** use a traditional stock-level panel. It starts from one monthly merged dataset and reshapes it into long form for the FE and DiD models.

## Shapes Used in Analysis

- Wide monthly dataset: **{len(wide_df)} rows x {len(wide_df.columns)} columns**
- Market regression sample after lags: **{len(market_df)} rows x {len(market_df.columns)} columns**
- Long stacked panel: **{len(long_df):,} rows x {len(long_df.columns)} columns**
- Variables in stacked panel: **{long_df['variable'].nunique()}**
- Monthly periods: **{wide_df['date'].nunique()}**

## What The Dataset Looks Like

### Wide monthly form used for market regressions

{wide_preview}

### Long stacked form used for FE and DiD

{long_preview}

## Interpretation

- If you ask, "Does lagged sentiment predict next month's aggregate market return?", that is a **time-series question**.
- If you ask, "Do sentiment variables behave differently from return and factor variables after major shocks?", that is handled with the **stacked panel FE / DiD setup**.
- Because each row in the long panel is a variable-month rather than a firm-month, this is best described as a **synthetic panel constructed from aggregate time-series data**.

## Output Files

- Figure: `{FIGURE_PATH}`
- Report: `{REPORT_PATH}`
"""

    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    wide_df = load_panel_as_wide(PANEL_PATH)
    long_df = load_long_panel(PANEL_PATH)
    market_df = build_market_regression_sample(wide_df)

    create_structure_figure(wide_df=wide_df, long_df=long_df, market_df=market_df)
    write_summary_report(wide_df=wide_df, long_df=long_df, market_df=market_df)

    print(f"Saved figure: {FIGURE_PATH}")
    print(f"Saved report: {REPORT_PATH}")


if __name__ == "__main__":
    main()