"""Generate M3 fixed-effects and DiD analysis deliverables.

Outputs:
- results/tables/m3_market_fe_results.csv
- results/tables/m3_entity_fe_results.csv
- results/tables/m3_did_results.csv
- results/figures/m3_treated_vs_control_trends.png
- results/figures/m3_did_coefficients.png
- results/figures/m3_market_model_fit.png
- results/reports/M3_interpretation.md
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan

from config_paths import FINAL_DATA_DIR, FIGURES_DIR, REPORTS_DIR, TABLES_DIR
from panel_format_utils import load_panel_as_wide


GFC_START = pd.Timestamp("2008-09-30")
COVID_START = pd.Timestamp("2020-03-31")


def ensure_long_panel(panel_path: Path) -> pd.DataFrame:
    """Return panel in tidy long format with date/variable/value columns."""
    raw = pd.read_csv(panel_path)
    if {"date", "variable", "value"}.issubset(raw.columns):
        long_df = raw.copy()
    else:
        if "date" not in raw.columns:
            raise ValueError("Input panel must include a date column.")
        value_cols = [c for c in raw.columns if c != "date"]
        long_df = raw.melt(id_vars="date", value_vars=value_cols, var_name="variable", value_name="value")

    long_df["date"] = pd.to_datetime(long_df["date"])
    long_df = long_df.sort_values(["variable", "date"]).reset_index(drop=True)
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
    return long_df


def coef_table(model) -> pd.DataFrame:
    """Return a tidy coefficient table with robust p-values."""
    out = pd.DataFrame(
        {
            "term": model.params.index,
            "coef": model.params.values,
            "std_err": model.bse.values,
            "t_stat": model.tvalues.values,
            "p_value": model.pvalues.values,
        }
    )
    ci = model.conf_int()
    out["ci_low"] = ci[0].values
    out["ci_high"] = ci[1].values
    return out


def build_market_model(wide_df: pd.DataFrame):
    """Estimate monthly return model with calendar-month fixed effects."""
    df = wide_df.copy()
    df = df.sort_values("date").reset_index(drop=True)
    df["sentiment_michigan_ics_l1"] = df["sentiment_michigan_ics"].shift(1)
    df["bull_bear_spread_l1"] = df["bull_bear_spread"].shift(1)
    df["month_of_year"] = df["date"].dt.month

    model_df = df.dropna(
        subset=[
            "mkt_ret",
            "sentiment_michigan_ics_l1",
            "bull_bear_spread_l1",
            "smb",
            "hml",
            "rmw",
            "cma",
            "month_of_year",
        ]
    ).copy()

    formula = (
        "mkt_ret ~ sentiment_michigan_ics_l1 + bull_bear_spread_l1 + "
        "smb + hml + rmw + cma + C(month_of_year)"
    )
    model = smf.ols(formula=formula, data=model_df).fit(cov_type="HC1")
    model_df["mkt_ret_fitted"] = model.fittedvalues

    return model, model_df


def build_panel_models(long_df: pd.DataFrame):
    """Estimate entity FE and DiD models on standardized long-form data."""
    sentiment_vars = {
        "sentiment_michigan_ics",
        "bullish_pct",
        "bearish_pct",
        "neutral_pct",
        "bull_bear_spread",
    }

    df = long_df.copy()
    df = df.dropna(subset=["value"]).copy()
    df["treated_sentiment"] = df["variable"].isin(sentiment_vars).astype(int)
    df["post_gfc"] = (df["date"] >= GFC_START).astype(int)
    df["post_covid"] = (df["date"] >= COVID_START).astype(int)

    grouped = df.groupby("variable")["value"]
    df["value_z"] = (df["value"] - grouped.transform("mean")) / grouped.transform("std")
    df["value_z"] = df["value_z"].replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["value_z"]).copy()

    entity_fe_formula = "value_z ~ treated_sentiment + post_gfc + post_covid + C(variable) + C(date)"
    entity_fe = smf.ols(formula=entity_fe_formula, data=df).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["variable"]},
    )

    did_formula = (
        "value_z ~ treated_sentiment:post_gfc + treated_sentiment:post_covid + "
        "C(variable) + C(date)"
    )
    did = smf.ols(formula=did_formula, data=df).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["variable"]},
    )

    return entity_fe, did, df


def run_diagnostics(market_model, market_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute BP and VIF diagnostics for market model predictors."""
    x_cols = [
        "sentiment_michigan_ics_l1",
        "bull_bear_spread_l1",
        "smb",
        "hml",
        "rmw",
        "cma",
    ]
    x = market_df[x_cols].copy()
    x_const = sm.add_constant(x)

    bp_lm, bp_lm_p, bp_f, bp_f_p = het_breuschpagan(market_model.resid, market_model.model.exog)
    bp_table = pd.DataFrame(
        [
            {
                "test": "Breusch-Pagan",
                "lm_stat": bp_lm,
                "lm_p_value": bp_lm_p,
                "f_stat": bp_f,
                "f_p_value": bp_f_p,
            }
        ]
    )

    vif_rows = []
    for i, col in enumerate(x_const.columns):
        if col == "const":
            continue
        vif_rows.append({"variable": col, "vif": variance_inflation_factor(x_const.values, i)})
    vif_table = pd.DataFrame(vif_rows)

    return bp_table, vif_table


def run_robustness_checks(wide_df: pd.DataFrame, panel_df: pd.DataFrame, did_base) -> pd.DataFrame:
    """Run three robustness checks and return a compact comparison table."""
    rows: list[dict] = []

    # Check 1: Alternative lag structures in market model (lags 1, 2, 3)
    lag_results = {}
    for lag in [1, 2, 3]:
        df = wide_df.copy().sort_values("date").reset_index(drop=True)
        df[f"sent_l{lag}"] = df["sentiment_michigan_ics"].shift(lag)
        df[f"bb_l{lag}"] = df["bull_bear_spread"].shift(lag)
        lag_df = df.dropna(subset=["mkt_ret", f"sent_l{lag}", f"bb_l{lag}", "smb", "hml", "rmw", "cma"]).copy()
        m = smf.ols(
            formula=f"mkt_ret ~ sent_l{lag} + bb_l{lag} + smb + hml + rmw + cma",
            data=lag_df,
        ).fit(cov_type="HC1")
        lag_results[lag] = float(m.params[f"sent_l{lag}"])

    rows.append(
        {
            "check": "alternative_lags",
            "metric": "sentiment_coef_lag1_vs_lag2_vs_lag3",
            "baseline_value": lag_results[1],
            "check_value": lag_results[2],
            "aux_value": lag_results[3],
            "interpretation": "Signs/magnitudes across lags indicate whether lag choice is sensitive.",
        }
    )

    # Check 2: Exclude acute COVID crash window from DiD
    excl = panel_df.loc[(panel_df["date"] < pd.Timestamp("2020-03-01")) | (panel_df["date"] > pd.Timestamp("2020-06-30"))].copy()
    did_excl = smf.ols(
        formula="value_z ~ treated_sentiment:post_gfc + treated_sentiment:post_covid + C(variable) + C(date)",
        data=excl,
    ).fit(cov_type="cluster", cov_kwds={"groups": excl["variable"]})
    rows.append(
        {
            "check": "exclude_covid_crash_window",
            "metric": "did_post_covid_interaction",
            "baseline_value": float(did_base.params.get("treated_sentiment:post_covid", np.nan)),
            "check_value": float(did_excl.params.get("treated_sentiment:post_covid", np.nan)),
            "aux_value": np.nan,
            "interpretation": "Close values imply COVID interaction is not driven only by the crash window.",
        }
    )

    # Check 3: Placebo DiD in pre-2008 period
    pre = panel_df.loc[panel_df["date"] < GFC_START].copy()
    placebo_cutoff = pd.Timestamp("2006-01-31")
    pre["post_placebo"] = (pre["date"] >= placebo_cutoff).astype(int)
    placebo = smf.ols(
        formula="value_z ~ treated_sentiment:post_placebo + C(variable) + C(date)",
        data=pre,
    ).fit(cov_type="cluster", cov_kwds={"groups": pre["variable"]})
    rows.append(
        {
            "check": "placebo_pre_gfc",
            "metric": "treated_sentiment:post_placebo",
            "baseline_value": 0.0,
            "check_value": float(placebo.params.get("treated_sentiment:post_placebo", np.nan)),
            "aux_value": float(placebo.pvalues.get("treated_sentiment:post_placebo", np.nan)),
            "interpretation": "Small/insignificant placebo effects support DiD identification assumptions.",
        }
    )

    return pd.DataFrame(rows)


def save_diagnostic_plots(market_model, market_df: pd.DataFrame) -> None:
    """Save residual diagnostic plots for market model."""
    resid = market_model.resid
    fitted = market_model.fittedvalues

    plt.figure(figsize=(10, 5))
    plt.scatter(fitted, resid, alpha=0.65)
    plt.axhline(0, color="black", linewidth=1)
    plt.xlabel("Fitted values")
    plt.ylabel("Residuals")
    plt.title("Residuals vs Fitted (Market Model)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3_residuals_vs_fitted.png", dpi=300, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 5))
    sm.qqplot(resid, line="45", fit=True)
    plt.title("Q-Q Plot of Market Model Residuals")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3_residuals_qq.png", dpi=300, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.histplot(resid, kde=True)
    plt.title("Residual Histogram (Market Model)")
    plt.xlabel("Residual")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3_residuals_hist.png", dpi=300, bbox_inches="tight")
    plt.close()


def build_comparison_table(entity_table: pd.DataFrame, did_table: pd.DataFrame) -> pd.DataFrame:
    """Build publication-style side-by-side comparison table for Model A and Model B."""
    a_terms = ["treated_sentiment", "post_gfc", "post_covid"]
    b_terms = ["treated_sentiment:post_gfc", "treated_sentiment:post_covid"]
    rows = []

    for term in sorted(set(a_terms + b_terms)):
        a = entity_table.loc[entity_table["term"] == term]
        b = did_table.loc[did_table["term"] == term]
        if not a.empty:
            a_row = a.iloc[0]
            a_cell = f"{a_row['coef']:.4f}{pstar(a_row['p_value'])} ({a_row['std_err']:.4f})"
        else:
            a_cell = ""
        if not b.empty:
            b_row = b.iloc[0]
            b_cell = f"{b_row['coef']:.4f}{pstar(b_row['p_value'])} ({b_row['std_err']:.4f})"
        else:
            b_cell = ""
        rows.append({"term": term, "Model_A_TWFE": a_cell, "Model_B_DiD": b_cell})

    rows.append(
        {
            "term": "Notes",
            "Model_A_TWFE": "Entity FE=Yes; Time FE=Yes; Clustered SE by variable=Yes",
            "Model_B_DiD": "Entity FE=Yes; Time FE=Yes; Clustered SE by variable=Yes",
        }
    )
    rows.append({"term": "Significance", "Model_A_TWFE": "*** p<0.01, ** p<0.05, * p<0.10", "Model_B_DiD": "*** p<0.01, ** p<0.05, * p<0.10"})

    return pd.DataFrame(rows)


def save_plots(panel_df: pd.DataFrame, did_table: pd.DataFrame, market_df: pd.DataFrame) -> None:
    """Create and save required visualizations for M3 deliverables."""
    sns.set_theme(style="whitegrid")

    # Plot 1: treated vs control standardized trends with crisis markers
    trend = panel_df.groupby(["date", "treated_sentiment"], as_index=False)["value_z"].mean()
    trend["group"] = np.where(trend["treated_sentiment"] == 1, "Sentiment variables", "Returns/factors")

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=trend, x="date", y="value_z", hue="group", linewidth=2.2)
    plt.axvline(GFC_START, color="#c0392b", linestyle="--", linewidth=1.8, label="GFC shock")
    plt.axvline(COVID_START, color="#8e44ad", linestyle="--", linewidth=1.8, label="COVID shock")
    plt.title("Standardized Series: Sentiment Group vs Control Group")
    plt.xlabel("Date")
    plt.ylabel("Standardized value (z-score)")
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3_treated_vs_control_trends.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Plot 2: DiD coefficients for the two crisis interactions
    keep_terms = {"treated_sentiment:post_gfc", "treated_sentiment:post_covid"}
    coef = did_table[did_table["term"].isin(keep_terms)].copy()
    coef["label"] = coef["term"].map(
        {
            "treated_sentiment:post_gfc": "Sentiment x Post-2008",
            "treated_sentiment:post_covid": "Sentiment x Post-COVID",
        }
    )

    plt.figure(figsize=(8, 5))
    sns.pointplot(data=coef, x="label", y="coef", linestyle="none", color="#1f77b4")
    for i, row in coef.reset_index(drop=True).iterrows():
        plt.plot([i, i], [row["ci_low"], row["ci_high"]], color="#1f77b4", linewidth=2)
    plt.axhline(0, color="black", linewidth=1)
    plt.title("Difference-in-Differences Effect Estimates")
    plt.xlabel("Interaction term")
    plt.ylabel("Estimated effect (standardized units)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3_did_coefficients.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Plot 3: observed vs fitted market return model
    plt.figure(figsize=(12, 6))
    plt.plot(market_df["date"], market_df["mkt_ret"], label="Observed mkt_ret", linewidth=1.8)
    plt.plot(market_df["date"], market_df["mkt_ret_fitted"], label="Fitted mkt_ret", linewidth=1.8)
    plt.axvline(GFC_START, color="#c0392b", linestyle="--", linewidth=1.6)
    plt.axvline(COVID_START, color="#8e44ad", linestyle="--", linewidth=1.6)
    plt.title("Market Return Model Fit with Crisis Markers")
    plt.xlabel("Date")
    plt.ylabel("Monthly market return (%)")
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3_market_model_fit.png", dpi=300, bbox_inches="tight")
    plt.close()


def pstar(p: float) -> str:
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def write_report(
    market_table: pd.DataFrame,
    entity_table: pd.DataFrame,
    did_table: pd.DataFrame,
    bp_table: pd.DataFrame,
    vif_table: pd.DataFrame,
    robustness_table: pd.DataFrame,
    market_nobs: int,
    panel_nobs: int,
) -> None:
    """Write an interpretation-first M3 markdown report."""
    key_market_terms = ["sentiment_michigan_ics_l1", "bull_bear_spread_l1", "smb", "hml", "rmw", "cma"]
    key_market = market_table[market_table["term"].isin(key_market_terms)].copy()

    did_gfc = did_table.loc[did_table["term"] == "treated_sentiment:post_gfc"].iloc[0]
    did_covid = did_table.loc[did_table["term"] == "treated_sentiment:post_covid"].iloc[0]

    lines = [
        "# M3 Interpretation: Fixed Effects and Difference-in-Differences",
        "",
        "## What we estimated",
        "1. **Calendar-month fixed effects model for market returns**",
        "   - Outcome: `mkt_ret`",
        "   - Key predictors: lagged Michigan sentiment and lagged AAII bull-bear spread",
        "   - Controls: `smb`, `hml`, `rmw`, `cma`",
        "   - Fixed effects: month-of-year dummies",
        "2. **Model A: Two-way fixed effects (entity and time) on the long panel**",
        "   - Outcome: standardized `value_z` in long-form panel",
        "   - Fixed effects: variable/entity dummies and date fixed effects",
        "   - Standard errors: clustered by entity (`variable`)",
        "   - Shock indicators: post-2008 and post-COVID",
        "3. **Difference-in-differences model for shocks**",
        "   - Treated group: sentiment series (`sentiment_michigan_ics`, AAII sentiment variables)",
        "   - Control group: market return and factor series",
        "   - Interactions: `treated_sentiment x post_gfc` and `treated_sentiment x post_covid`",
        "   - Date fixed effects included",
        "   - Standard errors: clustered by entity (`variable`)",
        "",
        "## Sample sizes",
        f"- Market FE observations: **{market_nobs}**",
        f"- Panel/DiD observations: **{panel_nobs}**",
        "",
        "## Main economic interpretation",
        "### 1) Predictive return model",
    ]

    for _, row in key_market.iterrows():
        lines.append(
            f"- `{row['term']}`: coef = {row['coef']:.4f}{pstar(row['p_value'])}, "
            f"p = {row['p_value']:.4f}, 95% CI [{row['ci_low']:.4f}, {row['ci_high']:.4f}]"
        )

    lines.extend(
        [
            "",
            "Interpretation in plain language:",
            "- A positive lagged sentiment coefficient would mean stronger confidence last month is associated with higher return this month.",
            "- A negative lagged bull-bear spread coefficient would support a contrarian story (too much bullishness predicts softer next-month returns).",
            "- Factor coefficients capture whether common risk channels still explain returns after sentiment is added.",
            "",
            "### 2) Entity fixed effects shock shifts",
        ]
    )

    for term in ["post_gfc", "post_covid"]:
        row = entity_table.loc[entity_table["term"] == term].iloc[0]
        lines.append(
            f"- `{term}`: coef = {row['coef']:.4f}{pstar(row['p_value'])}, "
            f"p = {row['p_value']:.4f}, 95% CI [{row['ci_low']:.4f}, {row['ci_high']:.4f}]"
        )

    lines.extend(
        [
            "",
            "Interpretation in plain language:",
            "- The entity FE model asks whether the average standardized level of series shifts after each macro shock, after controlling for each variable's own baseline level.",
            "",
            "### 3) DiD: differential effect on sentiment vs controls",
            f"- `treated_sentiment x post_gfc`: coef = {did_gfc['coef']:.4f}{pstar(did_gfc['p_value'])}, "
            f"p = {did_gfc['p_value']:.4f}, 95% CI [{did_gfc['ci_low']:.4f}, {did_gfc['ci_high']:.4f}]",
            f"- `treated_sentiment x post_covid`: coef = {did_covid['coef']:.4f}{pstar(did_covid['p_value'])}, "
            f"p = {did_covid['p_value']:.4f}, 95% CI [{did_covid['ci_low']:.4f}, {did_covid['ci_high']:.4f}]",
            "",
            "Interpretation in plain language:",
            "- Positive DiD interaction: sentiment series rose more (or fell less) than return/factor controls after that shock.",
            "- Negative DiD interaction: sentiment series weakened more than controls after that shock.",
            "",
            "## Diagnostics",
            f"- Breusch-Pagan p-value: **{bp_table.loc[0, 'lm_p_value']:.4f}**",
            f"- Max VIF among predictors: **{vif_table['vif'].max():.2f}**",
            "- Residual diagnostics saved as residual-vs-fitted, Q-Q, and histogram plots.",
            "",
            "Interpretation:",
            "- A low Breusch-Pagan p-value suggests heteroskedasticity risk; we therefore report robust/clustered SEs.",
            "- VIF values well below 10 reduce concern about severe multicollinearity.",
            "",
            "## Robustness checks",
        ]
    )

    for _, row in robustness_table.iterrows():
        lines.append(
            f"- `{row['check']}` ({row['metric']}): baseline={row['baseline_value']:.4f}, "
            f"check={row['check_value']:.4f}, aux={row['aux_value'] if pd.notna(row['aux_value']) else 'NA'}"
        )
        lines.append(f"  - {row['interpretation']}")

    lines.extend(
        [
            "",
            "## Visual evidence",
            "- `results/figures/m3_treated_vs_control_trends.png`: treated vs control paths with 2008 and 2020 markers.",
            "- `results/figures/m3_did_coefficients.png`: DiD point estimates and confidence intervals.",
            "- `results/figures/m3_market_model_fit.png`: observed vs fitted market returns.",
            "- `results/figures/m3_residuals_vs_fitted.png`: residual spread across fitted values.",
            "- `results/figures/m3_residuals_qq.png`: residual normality diagnostic.",
            "- `results/figures/m3_residuals_hist.png`: residual distribution check.",
            "",
            "## Applicability and limitations",
            "- The dataset has one aggregate market return series over time, so classic multi-firm panel FE on returns is not directly available.",
            "- The entity FE and DiD are applied on the stacked long panel where each variable acts as an entity.",
            "- This design is useful for testing shock sensitivity across groups of series, but it should not be interpreted as a firm-level causal panel model.",
            "- Robust (HC1) standard errors are used to reduce heteroskedasticity concerns.",
            "",
            "## Files generated for M3",
            "- `results/tables/m3_market_fe_results.csv`",
            "- `results/tables/m3_entity_fe_results.csv`",
            "- `results/tables/m3_did_results.csv`",
            "- `results/tables/m3_bp_test_results.csv`",
            "- `results/tables/m3_vif_results.csv`",
            "- `results/tables/m3_robustness_checks.csv`",
            "- `results/tables/m3_model_comparison_table.csv`",
            "- `results/figures/m3_treated_vs_control_trends.png`",
            "- `results/figures/m3_did_coefficients.png`",
            "- `results/figures/m3_market_model_fit.png`",
            "- `results/figures/m3_residuals_vs_fitted.png`",
            "- `results/figures/m3_residuals_qq.png`",
            "- `results/figures/m3_residuals_hist.png`",
        ]
    )

    report_path = REPORTS_DIR / "M3_interpretation.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    panel_path = FINAL_DATA_DIR / "analysis_panel.csv"
    if not panel_path.exists():
        raise FileNotFoundError(f"Missing required panel file: {panel_path}")

    wide_df = load_panel_as_wide(panel_path)
    long_df = ensure_long_panel(panel_path)

    market_model, market_model_df = build_market_model(wide_df)
    entity_fe_model, did_model, panel_df = build_panel_models(long_df)

    market_table = coef_table(market_model)
    entity_table = coef_table(entity_fe_model)
    did_table = coef_table(did_model)
    bp_table, vif_table = run_diagnostics(market_model, market_model_df)
    robustness_table = run_robustness_checks(wide_df, panel_df, did_model)
    comparison_table = build_comparison_table(entity_table, did_table)

    market_table.to_csv(TABLES_DIR / "m3_market_fe_results.csv", index=False)
    entity_table.to_csv(TABLES_DIR / "m3_entity_fe_results.csv", index=False)
    did_table.to_csv(TABLES_DIR / "m3_did_results.csv", index=False)
    bp_table.to_csv(TABLES_DIR / "m3_bp_test_results.csv", index=False)
    vif_table.to_csv(TABLES_DIR / "m3_vif_results.csv", index=False)
    robustness_table.to_csv(TABLES_DIR / "m3_robustness_checks.csv", index=False)
    comparison_table.to_csv(TABLES_DIR / "m3_model_comparison_table.csv", index=False)

    save_plots(panel_df=panel_df, did_table=did_table, market_df=market_model_df)
    save_diagnostic_plots(market_model, market_model_df)

    write_report(
        market_table=market_table,
        entity_table=entity_table,
        did_table=did_table,
        bp_table=bp_table,
        vif_table=vif_table,
        robustness_table=robustness_table,
        market_nobs=int(market_model.nobs),
        panel_nobs=int(did_model.nobs),
    )

    print("M3 analysis completed.")
    print(f"- Tables: {TABLES_DIR / 'm3_market_fe_results.csv'}")
    print(f"- Tables: {TABLES_DIR / 'm3_entity_fe_results.csv'}")
    print(f"- Tables: {TABLES_DIR / 'm3_did_results.csv'}")
    print(f"- Tables: {TABLES_DIR / 'm3_bp_test_results.csv'}")
    print(f"- Tables: {TABLES_DIR / 'm3_vif_results.csv'}")
    print(f"- Tables: {TABLES_DIR / 'm3_robustness_checks.csv'}")
    print(f"- Tables: {TABLES_DIR / 'm3_model_comparison_table.csv'}")
    print(f"- Figure: {FIGURES_DIR / 'm3_treated_vs_control_trends.png'}")
    print(f"- Figure: {FIGURES_DIR / 'm3_did_coefficients.png'}")
    print(f"- Figure: {FIGURES_DIR / 'm3_market_model_fit.png'}")
    print(f"- Figure: {FIGURES_DIR / 'm3_residuals_vs_fitted.png'}")
    print(f"- Figure: {FIGURES_DIR / 'm3_residuals_qq.png'}")
    print(f"- Figure: {FIGURES_DIR / 'm3_residuals_hist.png'}")
    print(f"- Report: {REPORTS_DIR / 'M3_interpretation.md'}")


if __name__ == "__main__":
    main()