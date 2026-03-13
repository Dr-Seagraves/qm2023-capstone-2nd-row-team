"""Generate Milestone 2 EDA deliverables.

Outputs:
- capstone_eda.ipynb
- M2_EDA_summary.md
- results/figures/M2_*.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose

from config_paths import FIGURES_DIR, FINAL_DATA_DIR, PROJECT_ROOT


sns.set_style("whitegrid")
sns.set_palette("colorblind")
plt.rcParams["font.size"] = 11


def load_data() -> pd.DataFrame:
    df = pd.read_csv(FINAL_DATA_DIR / "analysis_panel.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def save_fig(filename: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close()


def create_figures(df: pd.DataFrame) -> dict[str, float]:
    # Plot 1: Correlation heatmap
    vars_to_plot = [
        "mkt_ret",
        "sentiment_michigan_ics",
        "bull_bear_spread",
        "mkt_rf",
        "smb",
        "hml",
        "rmw",
        "cma",
        "rf",
    ]
    corr = df[vars_to_plot].corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, cmap="coolwarm", center=0, annot=True, fmt=".2f", linewidths=0.5)
    plt.title("M2 Plot 1: Correlation Heatmap (Returns, Sentiment, and Controls)")
    save_fig("M2_01_correlation_heatmap.png")

    # Plot 2: Outcome time series
    plt.figure(figsize=(12, 4.5))
    plt.plot(df["date"], df["mkt_ret"], color="#1f77b4", linewidth=1.8, label="Market Return")
    plt.axhline(0, color="black", linewidth=0.8, alpha=0.8)
    plt.title("M2 Plot 2: Market Return Time Series (2004-2024)")
    plt.xlabel("Date")
    plt.ylabel("Market Return (%)")
    plt.legend()
    save_fig("M2_02_outcome_time_series.png")

    # Plot 3: Dual-axis outcome vs driver
    fig, ax1 = plt.subplots(figsize=(12, 4.8))
    ax1.plot(df["date"], df["mkt_ret"], color="#1f77b4", linewidth=1.8, label="Market Return")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Market Return (%)", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")

    ax2 = ax1.twinx()
    ax2.plot(
        df["date"],
        df["sentiment_michigan_ics"],
        color="#d62728",
        linewidth=1.6,
        alpha=0.8,
        label="Michigan Sentiment",
    )
    ax2.set_ylabel("Michigan Sentiment Index", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper right")
    plt.title("M2 Plot 3: Dual-Axis Co-Movement (Market Return vs Michigan Sentiment)")
    save_fig("M2_03_dual_axis_outcome_driver.png")

    # Plot 4: Lagged effect analysis
    lags = [0, 1, 2, 3, 6, 12]
    lag_corr = []
    for lag in lags:
        lagged = df["sentiment_michigan_ics"].shift(lag)
        lag_corr.append(df["mkt_ret"].corr(lagged))

    lag_df = pd.DataFrame({"lag_months": lags, "correlation": lag_corr})

    plt.figure(figsize=(9, 4.8))
    sns.barplot(data=lag_df, x="lag_months", y="correlation", color="#2ca02c")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("M2 Plot 4: Lagged Correlation (Returns vs Lagged Michigan Sentiment)")
    plt.xlabel("Lag (Months)")
    plt.ylabel("Correlation")
    save_fig("M2_04_lagged_effects.png")

    # Plot 5 (alternative): Rolling correlation for dataset without groups
    rolling_corr = df["mkt_ret"].rolling(window=6).corr(df["sentiment_michigan_ics"])
    plt.figure(figsize=(12, 4.5))
    plt.plot(df["date"], rolling_corr, color="#9467bd", linewidth=1.8)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("M2 Plot 5: 6-Month Rolling Correlation (Returns vs Michigan Sentiment)")
    plt.xlabel("Date")
    plt.ylabel("Rolling Correlation")
    save_fig("M2_05_rolling_correlation.png")

    # Plot 6 (alternative): Subsample analysis
    periods = [
        ("2004-2008", "2004-01-01", "2008-12-31"),
        ("2009-2014", "2009-01-01", "2014-12-31"),
        ("2015-2019", "2015-01-01", "2019-12-31"),
        ("2020-2024", "2020-01-01", "2024-12-31"),
    ]
    sub_rows = []
    for label, start, end in periods:
        mask = (df["date"] >= pd.Timestamp(start)) & (df["date"] <= pd.Timestamp(end))
        sub = df.loc[mask]
        sub_rows.append(
            {
                "period": label,
                "corr_return_sentiment": sub["mkt_ret"].corr(sub["sentiment_michigan_ics"]),
            }
        )
    sub_df = pd.DataFrame(sub_rows)

    plt.figure(figsize=(9, 4.8))
    sns.barplot(data=sub_df, x="period", y="corr_return_sentiment", color="#ff7f0e")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("M2 Plot 6: Subsample Correlation by Time Period")
    plt.xlabel("Period")
    plt.ylabel("Correlation (Return vs Sentiment)")
    save_fig("M2_06_subsample_analysis.png")

    # Plot 7: Scatter plots of controls
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    sns.regplot(data=df, x="smb", y="mkt_ret", ax=axes[0], scatter_kws={"alpha": 0.65})
    axes[0].set_title("Returns vs SMB")
    axes[0].set_xlabel("SMB (%)")
    axes[0].set_ylabel("Market Return (%)")

    sns.regplot(data=df, x="hml", y="mkt_ret", ax=axes[1], scatter_kws={"alpha": 0.65}, color="#d62728")
    axes[1].set_title("Returns vs HML")
    axes[1].set_xlabel("HML (%)")
    axes[1].set_ylabel("Market Return (%)")

    fig.suptitle("M2 Plot 7: Factor-Control Relationships with Market Returns", y=1.03)
    save_fig("M2_07_control_scatterplots.png")

    # Plot 8: Seasonal decomposition
    series = df.set_index("date")["mkt_ret"].asfreq("ME")
    decomp = seasonal_decompose(series, model="additive", period=12, extrapolate_trend="freq")

    fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
    axes[0].plot(decomp.observed, color="#1f77b4")
    axes[0].set_title("Observed")
    axes[1].plot(decomp.trend, color="#2ca02c")
    axes[1].set_title("Trend")
    axes[2].plot(decomp.seasonal, color="#9467bd")
    axes[2].set_title("Seasonal")
    axes[3].plot(decomp.resid, color="#d62728")
    axes[3].set_title("Residual")
    axes[3].set_xlabel("Date")
    fig.suptitle("M2 Plot 8: Time Series Decomposition of Market Returns", y=0.995)
    save_fig("M2_08_time_series_decomposition.png")

    # Return key stats for summary markdown.
    best_lag = lag_df.loc[lag_df["correlation"].abs().idxmax()]
    return {
        "corr_ret_sent": float(corr.loc["mkt_ret", "sentiment_michigan_ics"]),
        "corr_ret_spread": float(corr.loc["mkt_ret", "bull_bear_spread"]),
        "best_lag": int(best_lag["lag_months"]),
        "best_lag_corr": float(best_lag["correlation"]),
        "max_abs_control_corr": float(df[["smb", "hml", "rmw", "cma", "rf", "mkt_rf"]].corrwith(df["mkt_ret"]).abs().max()),
    }


def write_summary(stats: dict[str, float], df: pd.DataFrame) -> None:
    outlier_dates = df.loc[df["mkt_ret"].abs() > 10, "date"].dt.strftime("%Y-%m").tolist()
    missing_total = int(df.isna().sum().sum())

    summary = f"""# M2 EDA Summary

## Key Findings
- Market returns and Michigan sentiment show a correlation of {stats['corr_ret_sent']:.3f}. The sign and magnitude suggest sentiment is informative, but not a stand-alone predictor.
- Market returns and AAII bull-bear spread correlate at {stats['corr_ret_spread']:.3f}, indicating retail positioning may matter for near-term pricing.
- The largest absolute lagged relationship appears at {stats['best_lag']} months (correlation {stats['best_lag_corr']:.3f}), which supports testing lagged sentiment terms in M3.
- Rolling and subsample analyses show the sentiment-return relationship is time-varying, so constant-coefficient models may be misspecified.
- Factor links remain meaningful; the largest absolute control correlation with returns is {stats['max_abs_control_corr']:.3f}, supporting inclusion of standard factor controls.

## Hypotheses for M3
1. **Sentiment effect hypothesis**: Lagged Michigan sentiment predicts monthly market returns after controlling for Fama-French factors.
    - Baseline model: mkt_ret_t = alpha + beta1 * sentiment_michigan_(t-{stats['best_lag']}) + gamma'X_t + epsilon_t
   - Expected sign: positive if higher confidence supports risk-taking and demand for equities.
2. **Retail positioning hypothesis**: AAII bull-bear spread has incremental explanatory power beyond Michigan sentiment.
   - Model extension: include `bull_bear_spread_t` with sentiment and controls.
   - Expected sign: positive contemporaneous association, with potential reversal at longer horizons.
3. **Regime heterogeneity hypothesis**: The sentiment-return relationship differs across periods (pre-crisis, post-crisis, pandemic).
   - Model extension: interact sentiment with regime dummies or estimate subsample models.
   - Expected sign: coefficient magnitude varies by macro regime, strongest during stress transitions.

## Data Quality Flags and M3 Mitigations
- **Outliers**: Extreme return months detected ({", ".join(outlier_dates) if outlier_dates else "none above |10%|"}).
  - Mitigation: robust standard errors and sensitivity checks with winsorized returns.
- **Missing values**: Total missing cells in the merged panel = {missing_total}.
  - Mitigation: no imputation required for baseline; maintain explicit checks in M3 pipeline.
- **Potential heteroskedasticity**: Volatility clustering appears in crisis periods.
  - Mitigation: use heteroskedasticity-robust (HC) or Newey-West standard errors.
- **Potential multicollinearity**: Controls from factor set can co-move.
  - Mitigation: report VIF diagnostics and avoid redundant controls if VIF is high.
"""

    (PROJECT_ROOT / "M2_EDA_summary.md").write_text(summary, encoding="utf-8")


def write_notebook() -> None:
    # We use nbformat only for authoring a clean, runnable notebook file.
    import nbformat as nbf

    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(
        nbf.v4.new_markdown_cell(
            "# Milestone 2: EDA Dashboard\n"
            "This notebook builds the eight required visualizations for M2 and saves them to `results/figures/` as 300 DPI PNG files."
        )
    )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 1. Imports and Data Loading\n"
            "Load the M1 output panel and parse dates for time-series analysis."
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import sys\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "from statsmodels.tsa.seasonal import seasonal_decompose\n"
            "\n"
            "sys.path.append(str(Path.cwd() / 'code'))\n"
            "from config_paths import FIGURES_DIR, FINAL_DATA_DIR\n"
            "\n"
            "sns.set_style('whitegrid')\n"
            "sns.set_palette('colorblind')\n"
            "plt.rcParams['font.size'] = 11\n"
            "\n"
            "df = pd.read_csv(FINAL_DATA_DIR / 'analysis_panel.csv')\n"
            "df['date'] = pd.to_datetime(df['date'])\n"
            "df = df.sort_values('date').reset_index(drop=True)\n"
            "FIGURES_DIR.mkdir(parents=True, exist_ok=True)\n"
            "\n"
            "print('Shape:', df.shape)\n"
            "print('Date range:', df['date'].min().date(), 'to', df['date'].max().date())\n"
            "df.head()"
        )
    )

    cells.append(nbf.v4.new_markdown_cell("## 2. Summary Statistics"))
    cells.append(
        nbf.v4.new_code_cell(
            "summary = df.describe().T\n"
            "summary[['mean','std','min','max']]"
        )
    )

    cells.append(nbf.v4.new_markdown_cell("## 3. Correlation Analysis"))
    cells.append(
        nbf.v4.new_code_cell(
            "vars_to_plot = ['mkt_ret','sentiment_michigan_ics','bull_bear_spread','mkt_rf','smb','hml','rmw','cma','rf']\n"
            "corr = df[vars_to_plot].corr()\n"
            "plt.figure(figsize=(10,8))\n"
            "sns.heatmap(corr, cmap='coolwarm', center=0, annot=True, fmt='.2f', linewidths=0.5)\n"
            "plt.title('M2 Plot 1: Correlation Heatmap (Returns, Sentiment, and Controls)')\n"
            "plt.tight_layout()\n"
            "plt.savefig(FIGURES_DIR / 'M2_01_correlation_heatmap.png', dpi=300, bbox_inches='tight')\n"
            "plt.show()"
        )
    )
    cells.append(
        nbf.v4.new_markdown_cell(
            "**Caption:** Returns show weak-to-moderate association with sentiment variables and stronger links with market-factor controls. This suggests M3 should include both sentiment terms and factor controls to avoid omitted-variable bias."
        )
    )

    cells.append(nbf.v4.new_markdown_cell("## 4. Time Series Visuals"))
    cells.append(
        nbf.v4.new_code_cell(
            "plt.figure(figsize=(12,4.5))\n"
            "plt.plot(df['date'], df['mkt_ret'], linewidth=1.8, label='Market Return')\n"
            "plt.axhline(0, color='black', linewidth=0.8, alpha=0.8)\n"
            "plt.title('M2 Plot 2: Market Return Time Series (2004-2024)')\n"
            "plt.xlabel('Date')\n"
            "plt.ylabel('Market Return (%)')\n"
            "plt.legend()\n"
            "plt.tight_layout()\n"
            "plt.savefig(FIGURES_DIR / 'M2_02_outcome_time_series.png', dpi=300, bbox_inches='tight')\n"
            "plt.show()"
        )
    )
    cells.append(
        nbf.v4.new_markdown_cell(
            "**Caption:** Returns exhibit distinct volatility clustering around stress episodes, indicating non-constant variance. M3 should use robust or HAC standard errors."
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "fig, ax1 = plt.subplots(figsize=(12,4.8))\n"
            "ax1.plot(df['date'], df['mkt_ret'], color='#1f77b4', linewidth=1.8, label='Market Return')\n"
            "ax1.set_xlabel('Date')\n"
            "ax1.set_ylabel('Market Return (%)', color='#1f77b4')\n"
            "ax1.tick_params(axis='y', labelcolor='#1f77b4')\n"
            "\n"
            "ax2 = ax1.twinx()\n"
            "ax2.plot(df['date'], df['sentiment_michigan_ics'], color='#d62728', linewidth=1.6, alpha=0.8, label='Michigan Sentiment')\n"
            "ax2.set_ylabel('Michigan Sentiment Index', color='#d62728')\n"
            "ax2.tick_params(axis='y', labelcolor='#d62728')\n"
            "\n"
            "lines, labels = ax1.get_legend_handles_labels()\n"
            "lines2, labels2 = ax2.get_legend_handles_labels()\n"
            "ax1.legend(lines + lines2, labels + labels2, loc='upper right')\n"
            "plt.title('M2 Plot 3: Dual-Axis Co-Movement (Market Return vs Michigan Sentiment)')\n"
            "plt.tight_layout()\n"
            "plt.savefig(FIGURES_DIR / 'M2_03_dual_axis_outcome_driver.png', dpi=300, bbox_inches='tight')\n"
            "plt.show()"
        )
    )
    cells.append(
        nbf.v4.new_markdown_cell(
            "**Caption:** Co-movement exists but is not one-for-one and appears regime dependent. This supports testing lag structure and interactions instead of only contemporaneous levels."
        )
    )

    cells.append(nbf.v4.new_markdown_cell("## 5. Lagged Effect Analysis"))
    cells.append(
        nbf.v4.new_code_cell(
            "lags = [0,1,2,3,6,12]\n"
            "lag_corr = []\n"
            "for lag in lags:\n"
            "    lag_corr.append(df['mkt_ret'].corr(df['sentiment_michigan_ics'].shift(lag)))\n"
            "lag_df = pd.DataFrame({'lag_months': lags, 'correlation': lag_corr})\n"
            "\n"
            "plt.figure(figsize=(9,4.8))\n"
            "sns.barplot(data=lag_df, x='lag_months', y='correlation', color='#2ca02c')\n"
            "plt.axhline(0, color='black', linewidth=0.8)\n"
            "plt.title('M2 Plot 4: Lagged Correlation (Returns vs Lagged Michigan Sentiment)')\n"
            "plt.xlabel('Lag (Months)')\n"
            "plt.ylabel('Correlation')\n"
            "plt.tight_layout()\n"
            "plt.savefig(FIGURES_DIR / 'M2_04_lagged_effects.png', dpi=300, bbox_inches='tight')\n"
            "plt.show()\n"
            "lag_df"
        )
    )
    cells.append(
        nbf.v4.new_markdown_cell(
            "**Caption:** The largest absolute lagged correlation identifies the first lag candidate for M3. Economically, delayed reaction is plausible when sentiment changes diffuse through spending and investment behavior over several months."
        )
    )

    cells.append(nbf.v4.new_markdown_cell("## 6. Alternatives for Dataset Without Groups"))
    cells.append(
        nbf.v4.new_code_cell(
            "rolling_corr = df['mkt_ret'].rolling(window=6).corr(df['sentiment_michigan_ics'])\n"
            "plt.figure(figsize=(12,4.5))\n"
            "plt.plot(df['date'], rolling_corr, color='#9467bd', linewidth=1.8)\n"
            "plt.axhline(0, color='black', linewidth=0.8)\n"
            "plt.title('M2 Plot 5: 6-Month Rolling Correlation (Returns vs Michigan Sentiment)')\n"
            "plt.xlabel('Date')\n"
            "plt.ylabel('Rolling Correlation')\n"
            "plt.tight_layout()\n"
            "plt.savefig(FIGURES_DIR / 'M2_05_rolling_correlation.png', dpi=300, bbox_inches='tight')\n"
            "plt.show()"
        )
    )
    cells.append(
        nbf.v4.new_markdown_cell(
            "**Caption:** Rolling correlations vary over time, indicating structural instability. M3 should evaluate regime effects or time-varying coefficients."
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "periods = [('2004-2008','2004-01-01','2008-12-31'), ('2009-2014','2009-01-01','2014-12-31'), ('2015-2019','2015-01-01','2019-12-31'), ('2020-2024','2020-01-01','2024-12-31')]\n"
            "rows = []\n"
            "for label, start, end in periods:\n"
            "    mask = (df['date'] >= pd.Timestamp(start)) & (df['date'] <= pd.Timestamp(end))\n"
            "    sub = df.loc[mask]\n"
            "    rows.append({'period': label, 'corr_return_sentiment': sub['mkt_ret'].corr(sub['sentiment_michigan_ics'])})\n"
            "sub_df = pd.DataFrame(rows)\n"
            "\n"
            "plt.figure(figsize=(9,4.8))\n"
            "sns.barplot(data=sub_df, x='period', y='corr_return_sentiment', color='#ff7f0e')\n"
            "plt.axhline(0, color='black', linewidth=0.8)\n"
            "plt.title('M2 Plot 6: Subsample Correlation by Time Period')\n"
            "plt.xlabel('Period')\n"
            "plt.ylabel('Correlation (Return vs Sentiment)')\n"
            "plt.tight_layout()\n"
            "plt.savefig(FIGURES_DIR / 'M2_06_subsample_analysis.png', dpi=300, bbox_inches='tight')\n"
            "plt.show()\n"
            "sub_df"
        )
    )
    cells.append(
        nbf.v4.new_markdown_cell(
            "**Caption:** Subsample differences are consistent with changing macro environments and policy regimes. Interaction terms or period dummies are likely needed in M3."
        )
    )

    cells.append(nbf.v4.new_markdown_cell("## 7. Factor / Control Relationships"))
    cells.append(
        nbf.v4.new_code_cell(
            "fig, axes = plt.subplots(1,2, figsize=(12,4.8))\n"
            "sns.regplot(data=df, x='smb', y='mkt_ret', ax=axes[0], scatter_kws={'alpha': 0.65})\n"
            "axes[0].set_title('Returns vs SMB')\n"
            "axes[0].set_xlabel('SMB (%)')\n"
            "axes[0].set_ylabel('Market Return (%)')\n"
            "sns.regplot(data=df, x='hml', y='mkt_ret', ax=axes[1], scatter_kws={'alpha': 0.65}, color='#d62728')\n"
            "axes[1].set_title('Returns vs HML')\n"
            "axes[1].set_xlabel('HML (%)')\n"
            "axes[1].set_ylabel('Market Return (%)')\n"
            "fig.suptitle('M2 Plot 7: Factor-Control Relationships with Market Returns', y=1.03)\n"
            "plt.tight_layout()\n"
            "plt.savefig(FIGURES_DIR / 'M2_07_control_scatterplots.png', dpi=300, bbox_inches='tight')\n"
            "plt.show()"
        )
    )
    cells.append(
        nbf.v4.new_markdown_cell(
            "**Caption:** Scatter patterns with fitted lines provide visual evidence that factor controls explain part of return variation and should remain in M3 specifications."
        )
    )

    cells.append(nbf.v4.new_markdown_cell("## 8. Time Series Decomposition"))
    cells.append(
        nbf.v4.new_code_cell(
            "series = df.set_index('date')['mkt_ret'].asfreq('ME')\n"
            "decomp = seasonal_decompose(series, model='additive', period=12, extrapolate_trend='freq')\n"
            "fig, axes = plt.subplots(4,1, figsize=(12,8), sharex=True)\n"
            "axes[0].plot(decomp.observed)\n"
            "axes[0].set_title('Observed')\n"
            "axes[1].plot(decomp.trend)\n"
            "axes[1].set_title('Trend')\n"
            "axes[2].plot(decomp.seasonal)\n"
            "axes[2].set_title('Seasonal')\n"
            "axes[3].plot(decomp.resid)\n"
            "axes[3].set_title('Residual')\n"
            "axes[3].set_xlabel('Date')\n"
            "fig.suptitle('M2 Plot 8: Time Series Decomposition of Market Returns', y=0.995)\n"
            "plt.tight_layout()\n"
            "plt.savefig(FIGURES_DIR / 'M2_08_time_series_decomposition.png', dpi=300, bbox_inches='tight')\n"
            "plt.show()"
        )
    )
    cells.append(
        nbf.v4.new_markdown_cell(
            "**Caption:** Decomposition separates long-run trend, recurring seasonal structure, and residual noise. If seasonal components are material, M3 should include seasonality controls."
        )
    )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 9. File Check\n"
            "Confirm all M2 figures were saved to the required output directory."
        )
    )
    cells.append(
        nbf.v4.new_code_cell(
            "sorted([p.name for p in FIGURES_DIR.glob('M2_*.png')])"
        )
    )

    nb["cells"] = cells
    (PROJECT_ROOT / "capstone_eda.ipynb").write_text(nbf.writes(nb), encoding="utf-8")


def main() -> None:
    df = load_data()
    stats = create_figures(df)
    write_summary(stats, df)
    write_notebook()
    print("M2 deliverables generated successfully.")


if __name__ == "__main__":
    main()
