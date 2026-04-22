"""Run a single-series event study for the major macro shocks.

Outputs:
- results/tables/time_series_event_study_window_results.csv
- results/tables/time_series_event_study_monthly_path.csv
- results/tables/time_series_event_study_benchmark_models.csv
- results/figures/time_series_event_study_paths.png
- results/figures/time_series_event_study_window_bars.png
- results/reports/time_series_event_study_summary.md

Method:
- Use the aggregate monthly market return series only.
- For each shock, estimate a pre-event benchmark model on a rolling pre-event
  estimation window using lagged sentiment and lagged factor controls.
- Compute abnormal returns in the event window as actual minus benchmark-predicted returns.
- Report cumulative abnormal returns (CARs) for several symmetric event windows.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from scipy.stats import norm

from config_paths import FIGURES_DIR, FINAL_DATA_DIR, REPORTS_DIR, TABLES_DIR


DATA_PATH = FINAL_DATA_DIR / "analysis_event_study_ready.csv"
WINDOW_RESULTS_PATH = TABLES_DIR / "time_series_event_study_window_results.csv"
MONTHLY_PATH_PATH = TABLES_DIR / "time_series_event_study_monthly_path.csv"
BENCHMARK_TABLE_PATH = TABLES_DIR / "time_series_event_study_benchmark_models.csv"
PATH_FIGURE_PATH = FIGURES_DIR / "time_series_event_study_paths.png"
BAR_FIGURE_PATH = FIGURES_DIR / "time_series_event_study_window_bars.png"
SUMMARY_PATH = REPORTS_DIR / "time_series_event_study_summary.md"

REGRESSORS = [
    "sentiment_michigan_ics_l1",
    "bull_bear_spread_l1",
    "smb_l1",
    "hml_l1",
    "rmw_l1",
    "cma_l1",
]

EVENTS = [
    {
        "name": "GFC",
        "label": "2008 Financial Crisis",
        "date": pd.Timestamp("2008-09-30"),
        "event_time_col": "event_time_gfc",
    },
    {
        "name": "COVID",
        "label": "COVID Shock",
        "date": pd.Timestamp("2020-03-31"),
        "event_time_col": "event_time_covid",
    },
]

ESTIMATION_START = -60
ESTIMATION_END = -13
PLOT_WINDOW = 12
SUMMARY_WINDOWS = [0, 1, 3, 6, 12]


def pstar(p_value: float) -> str:
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


def load_event_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def fit_benchmark_model(df: pd.DataFrame, event_time_col: str):
    estimation_df = df.loc[df[event_time_col].between(ESTIMATION_START, ESTIMATION_END)].dropna(
        subset=["mkt_ret", *REGRESSORS]
    ).copy()
    if len(estimation_df) < 24:
        raise ValueError(f"Too few estimation observations for {event_time_col}: {len(estimation_df)}")

    formula = "mkt_ret ~ " + " + ".join(REGRESSORS)
    model = smf.ols(formula=formula, data=estimation_df).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    estimation_df["fitted"] = model.predict(estimation_df)
    residual_std = float((estimation_df["mkt_ret"] - estimation_df["fitted"]).std(ddof=1))
    return model, estimation_df, residual_std


def build_event_path(df: pd.DataFrame, event: dict, model, residual_std: float) -> pd.DataFrame:
    event_df = df.loc[df[event["event_time_col"]].between(-PLOT_WINDOW, PLOT_WINDOW)].dropna(
        subset=["mkt_ret", *REGRESSORS]
    ).copy()
    event_df["expected_ret"] = model.predict(event_df)
    event_df["abnormal_ret"] = event_df["mkt_ret"] - event_df["expected_ret"]
    event_df["car"] = event_df["abnormal_ret"].cumsum()
    event_df["sar"] = event_df["abnormal_ret"] / residual_std if residual_std > 0 else np.nan
    event_df["event_name"] = event["name"]
    event_df["event_label"] = event["label"]
    event_df["event_month"] = event_df[event["event_time_col"]]
    return event_df[
        [
            "event_name",
            "event_label",
            "date",
            "event_month",
            "mkt_ret",
            "expected_ret",
            "abnormal_ret",
            "car",
            "sar",
        ]
    ].copy()


def summarize_event_windows(event_path: pd.DataFrame, residual_std: float) -> pd.DataFrame:
    rows = []
    for half_window in SUMMARY_WINDOWS:
        window_df = event_path.loc[event_path["event_month"].between(-half_window, half_window)].copy()
        n_obs = len(window_df)
        car = float(window_df["abnormal_ret"].sum())
        aar = float(window_df["abnormal_ret"].mean()) if n_obs > 0 else np.nan

        if residual_std > 0 and n_obs > 0:
            car_se = residual_std * math.sqrt(n_obs)
            car_t = car / car_se
            car_p = 2 * (1 - norm.cdf(abs(car_t)))
        else:
            car_se = np.nan
            car_t = np.nan
            car_p = np.nan

        rows.append(
            {
                "event_name": event_path["event_name"].iloc[0],
                "event_label": event_path["event_label"].iloc[0],
                "window": f"[-{half_window}, +{half_window}]",
                "window_half_width": half_window,
                "n_obs": n_obs,
                "average_abnormal_return": aar,
                "car": car,
                "car_se": car_se,
                "car_t_stat": car_t,
                "car_p_value": car_p,
                "significance": pstar(car_p) if pd.notna(car_p) else "",
            }
        )

    return pd.DataFrame(rows)


def benchmark_table(event: dict, model, estimation_df: pd.DataFrame, residual_std: float) -> pd.DataFrame:
    rows = []
    conf_int = model.conf_int()
    for term in ["Intercept", *REGRESSORS]:
        rows.append(
            {
                "event_name": event["name"],
                "event_label": event["label"],
                "term": term,
                "coef": float(model.params[term]),
                "std_err": float(model.bse[term]),
                "t_stat": float(model.tvalues[term]),
                "p_value": float(model.pvalues[term]),
                "ci_low": float(conf_int.loc[term, 0]),
                "ci_high": float(conf_int.loc[term, 1]),
                "n_obs": int(model.nobs),
                "r_squared": float(model.rsquared),
                "residual_std": residual_std,
                "estimation_start": estimation_df["date"].min().date().isoformat(),
                "estimation_end": estimation_df["date"].max().date().isoformat(),
            }
        )
    return pd.DataFrame(rows)


def plot_event_paths(monthly_paths: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharex=True)

    for row_index, event_name in enumerate(["GFC", "COVID"]):
        event_df = monthly_paths.loc[monthly_paths["event_name"] == event_name].copy()

        ax_left = axes[row_index, 0]
        ax_left.plot(event_df["event_month"], event_df["mkt_ret"], label="Actual return", linewidth=2)
        ax_left.plot(event_df["event_month"], event_df["expected_ret"], label="Expected return", linewidth=2)
        ax_left.axvline(0, color="black", linestyle="--", linewidth=1)
        ax_left.axhline(0, color="black", linewidth=0.8, alpha=0.4)
        ax_left.set_title(f"{event_df['event_label'].iloc[0]}: Actual vs Expected")
        ax_left.set_ylabel("Monthly return (%)")
        ax_left.legend(loc="best")

        ax_right = axes[row_index, 1]
        ax_right.plot(event_df["event_month"], event_df["car"], color="#c0392b", linewidth=2.3)
        ax_right.axvline(0, color="black", linestyle="--", linewidth=1)
        ax_right.axhline(0, color="black", linewidth=0.8, alpha=0.4)
        ax_right.set_title(f"{event_df['event_label'].iloc[0]}: Cumulative Abnormal Return")
        ax_right.set_ylabel("CAR (%)")

    for ax in axes.flat:
        ax.set_xlabel("Event month")

    fig.suptitle("Single-Series Event Study Around the Two Macro Shocks", fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.savefig(PATH_FIGURE_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_window_bars(window_results: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")
    plot_df = window_results.copy()
    plot_df["window_label"] = plot_df["window"]

    plt.figure(figsize=(12, 6))
    sns.barplot(data=plot_df, x="window_label", y="car", hue="event_label")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("Cumulative Abnormal Returns by Event Window")
    plt.xlabel("Event window")
    plt.ylabel("CAR (%)")
    plt.tight_layout()
    plt.savefig(BAR_FIGURE_PATH, dpi=300, bbox_inches="tight")
    plt.close()


def write_summary(window_results: pd.DataFrame, benchmark_results: pd.DataFrame) -> None:
    lines = [
        "# Time-Series Event Study Summary",
        "",
        "## Method",
        "",
        "This is a single-series event study on aggregate monthly market returns.",
        "For each shock, expected returns are estimated from a pre-event benchmark model:",
        "",
        "- Outcome: `mkt_ret`",
        "- Regressors: lagged Michigan sentiment, lagged AAII bull-bear spread, and lagged Fama-French controls (`smb_l1`, `hml_l1`, `rmw_l1`, `cma_l1`)",
        "- Estimation window: months `-60` through `-13` before the event",
        "- Inference in the benchmark model: HAC/Newey-West standard errors with 3 lags",
        "- Event study outputs: abnormal returns and cumulative abnormal returns in the event window",
        "",
        "This is the correct design for this repository because the data are a single aggregate monthly time series, not a multi-entity panel.",
        "",
        "## Main Results",
        "",
    ]

    for event_name in ["GFC", "COVID"]:
        event_rows = window_results.loc[window_results["event_name"] == event_name].copy()
        event_label = event_rows["event_label"].iloc[0]
        lines.append(f"### {event_label}")
        for _, row in event_rows.iterrows():
            lines.append(
                f"- Window {row['window']}: CAR = {row['car']:.3f}{row['significance']}, "
                f"t = {row['car_t_stat']:.3f}, p = {row['car_p_value']:.4f}"
            )
        lines.append("")

    lines.extend(
        [
            "## Benchmark Model Fit",
            "",
        ]
    )

    benchmark_summary = (
        benchmark_results.groupby(["event_name", "event_label"], as_index=False)
        .agg({"n_obs": "first", "r_squared": "first", "residual_std": "first", "estimation_start": "first", "estimation_end": "first"})
    )
    for _, row in benchmark_summary.iterrows():
        lines.append(
            f"- {row['event_label']}: estimation window {row['estimation_start']} to {row['estimation_end']}, "
            f"N = {int(row['n_obs'])}, R-squared = {row['r_squared']:.3f}, residual SD = {row['residual_std']:.3f}"
        )

    lines.extend(
        [
            "",
            "## Files Generated",
            f"- Table: `{WINDOW_RESULTS_PATH}`",
            f"- Table: `{MONTHLY_PATH_PATH}`",
            f"- Table: `{BENCHMARK_TABLE_PATH}`",
            f"- Figure: `{PATH_FIGURE_PATH}`",
            f"- Figure: `{BAR_FIGURE_PATH}`",
        ]
    )

    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df = load_event_data(DATA_PATH)

    all_window_results = []
    all_monthly_paths = []
    all_benchmark_tables = []

    for event in EVENTS:
        model, estimation_df, residual_std = fit_benchmark_model(df, event["event_time_col"])
        event_path = build_event_path(df, event, model, residual_std)
        window_results = summarize_event_windows(event_path, residual_std)
        benchmark_results = benchmark_table(event, model, estimation_df, residual_std)

        all_monthly_paths.append(event_path)
        all_window_results.append(window_results)
        all_benchmark_tables.append(benchmark_results)

    monthly_paths = pd.concat(all_monthly_paths, ignore_index=True)
    window_results = pd.concat(all_window_results, ignore_index=True)
    benchmark_results = pd.concat(all_benchmark_tables, ignore_index=True)

    monthly_paths.to_csv(MONTHLY_PATH_PATH, index=False)
    window_results.to_csv(WINDOW_RESULTS_PATH, index=False)
    benchmark_results.to_csv(BENCHMARK_TABLE_PATH, index=False)

    plot_event_paths(monthly_paths)
    plot_window_bars(window_results)
    write_summary(window_results, benchmark_results)

    print(f"Saved table: {WINDOW_RESULTS_PATH}")
    print(f"Saved table: {MONTHLY_PATH_PATH}")
    print(f"Saved table: {BENCHMARK_TABLE_PATH}")
    print(f"Saved figure: {PATH_FIGURE_PATH}")
    print(f"Saved figure: {BAR_FIGURE_PATH}")
    print(f"Saved report: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()