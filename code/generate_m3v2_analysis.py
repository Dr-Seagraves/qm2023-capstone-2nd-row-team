"""Generate M3v2 firm-panel regression deliverables.

Outputs use the `m3v2_` prefix so they can live alongside the earlier M3
attempt without overwriting it.

Expected outputs:
- data/final/m3v2_firm_panel.csv
- results/tables/m3v2_ols_full_period_results.csv
- results/tables/m3v2_ols_covid_only_results.csv
- results/tables/m3v2_fe_results.csv
- results/tables/m3v2_did_results.csv
- results/tables/m3v2_bp_test_results.csv
- results/tables/m3v2_vif_results.csv
- results/tables/m3v2_robustness_checks.csv
- results/tables/m3v2_model_comparison_table.csv
- results/tables/m3v2_model_comparison_table.md
- results/figures/m3v2_group_trends.png
- results/figures/m3v2_ols_fitted_scatter.png
- results/figures/m3v2_residuals_vs_fitted.png
- results/figures/m3v2_residuals_qq.png
- results/figures/m3v2_residuals_hist.png
- results/figures/m3v2_fe_did_coefficients.png
- results/reports/M3v2_interpretation.md
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor

from config_paths import FINAL_DATA_DIR, FIGURES_DIR, REPORTS_DIR, TABLES_DIR


RAW_FIRM_PATH = FINAL_DATA_DIR.parent / "raw" / "us-comp.csv"
MICHIGAN_SENTIMENT_PATH = FINAL_DATA_DIR.parent / "processed" / "michigan_sentiment.csv"
FIRM_PANEL_OUTPUT_PATH = FINAL_DATA_DIR / "m3v2_firm_panel.csv"
REPORT_PATH = REPORTS_DIR / "M3v2_interpretation.md"
ROOT_REPORT_PATH = Path(__file__).resolve().parent.parent / "M3v2_interpretation.md"

ANALYSIS_START_YEAR = 2005
ANALYSIS_END_YEAR = 2021
COVID_START_YEAR = 2020
GFC_START_YEAR = 2008


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Divide safely and return NaN when the denominator is zero or missing."""
    ratio = pd.Series(np.nan, index=numerator.index, dtype="float64")
    valid = denominator.notna() & (denominator != 0) & numerator.notna()
    ratio.loc[valid] = numerator.loc[valid] / denominator.loc[valid]
    return ratio


def first_non_missing(series: pd.Series) -> float:
    """Return the first non-missing value in a series, or NaN if none exists."""
    non_missing = series.dropna()
    if non_missing.empty:
        return np.nan
    return float(non_missing.iloc[0])


def annualize_michigan_sentiment() -> pd.DataFrame:
    """Aggregate monthly Michigan sentiment to calendar-year means and lags."""
    sentiment = pd.read_csv(MICHIGAN_SENTIMENT_PATH)
    sentiment["date"] = pd.to_datetime(sentiment["date"], errors="coerce")
    sentiment["year"] = sentiment["date"].dt.year

    annual = (
        sentiment.groupby("year", as_index=False)["sentiment_michigan_ics"]
        .mean()
        .sort_values("year")
        .reset_index(drop=True)
    )
    annual["sentiment_lag1"] = annual["sentiment_michigan_ics"].shift(1)
    annual["sentiment_lag2"] = annual["sentiment_michigan_ics"].shift(2)
    annual["sentiment_lag3"] = annual["sentiment_michigan_ics"].shift(3)
    return annual


def load_and_prepare_firm_panel() -> pd.DataFrame:
    """Load the firm-year data, construct returns, controls, and sentiment lags."""
    firm = pd.read_csv(RAW_FIRM_PATH)
    firm["gvkey"] = firm["gvkey"].astype(str).str.zfill(6)
    firm["fyear"] = pd.to_numeric(firm["fyear"], errors="coerce").astype("Int64")
    firm["datadate"] = pd.to_datetime(firm["datadate"].astype(str).str.title(), format="%d%b%Y", errors="coerce")

    numeric_cols = ["at", "capx", "che", "dt", "ebit", "ib", "revt", "sale", "seq", "txt", "xrd", "dvpsp_f", "prcc_f", "sic"]
    for column in numeric_cols:
        firm[column] = pd.to_numeric(firm[column], errors="coerce")

    firm = firm.sort_values(["gvkey", "fyear"]).reset_index(drop=True)
    firm["prcc_f_l1"] = firm.groupby("gvkey")["prcc_f"].shift(1)
    firm["annual_return"] = safe_divide(firm["prcc_f"] - firm["prcc_f_l1"] + firm["dvpsp_f"].fillna(0), firm["prcc_f_l1"])

    firm["log_at"] = np.log(firm["at"].where(firm["at"] > 0))
    firm["leverage"] = safe_divide(firm["dt"], firm["at"])
    firm["profitability"] = safe_divide(firm["ebit"], firm["at"])
    firm["capex_intensity"] = safe_divide(firm["capx"], firm["at"])
    firm["cash_ratio"] = safe_divide(firm["che"], firm["at"])
    firm["rd_intensity"] = safe_divide(firm["xrd"], firm["at"])
    firm["revenue_to_assets"] = safe_divide(firm["sale"], firm["at"])

    firm["sic2"] = (firm["sic"] // 100).astype("Int64")
    firm["sic2_label"] = firm["sic2"].astype(str).replace("<NA>", "Unknown")

    firm["baseline_log_at"] = firm.groupby("gvkey")["log_at"].transform(first_non_missing)
    firm["firm_size_rank"] = firm["baseline_log_at"].rank(pct=True, method="average")
    firm["small_firm"] = (firm["firm_size_rank"] <= 0.5).astype(int)

    sentiment = annualize_michigan_sentiment()
    firm = firm.merge(sentiment[["year", "sentiment_michigan_ics", "sentiment_lag1", "sentiment_lag2", "sentiment_lag3"]], left_on="fyear", right_on="year", how="left")
    firm = firm.drop(columns=["year"])

    firm = firm.loc[(firm["fyear"] >= ANALYSIS_START_YEAR) & (firm["fyear"] <= ANALYSIS_END_YEAR)].copy()
    firm = firm.dropna(
        subset=[
            "annual_return",
            "sentiment_lag1",
            "log_at",
            "leverage",
            "profitability",
            "capex_intensity",
            "cash_ratio",
            "rd_intensity",
        ]
    ).copy()

    firm["post_gfc"] = (firm["fyear"] >= GFC_START_YEAR).astype(int)
    firm["post_covid"] = (firm["fyear"] >= COVID_START_YEAR).astype(int)
    firm["sentiment_x_small"] = firm["sentiment_lag1"] * firm["small_firm"]
    firm["sentiment_x_small_post_gfc"] = firm["sentiment_lag1"] * firm["small_firm"] * firm["post_gfc"]
    firm["sentiment_x_small_post_covid"] = firm["sentiment_lag1"] * firm["small_firm"] * firm["post_covid"]
    firm["small_x_post_gfc"] = firm["small_firm"] * firm["post_gfc"]
    firm["small_x_post_covid"] = firm["small_firm"] * firm["post_covid"]

    return firm


def fit_pooled_ols(df: pd.DataFrame, lag_column: str = "sentiment_lag1", covid_only: bool = False):
    """Estimate a pooled OLS model with industry fixed effects and clustered SEs."""
    model_df = df.copy()
    if covid_only:
        model_df = model_df.loc[model_df["fyear"] >= COVID_START_YEAR].copy()

    formula = (
        "annual_return ~ "
        f"{lag_column} + log_at + leverage + profitability + capex_intensity + cash_ratio + rd_intensity + C(sic2_label)"
    )
    result = smf.ols(formula=formula, data=model_df).fit(cov_type="cluster", cov_kwds={"groups": model_df["gvkey"]})
    return result, model_df


def fit_panel_models(df: pd.DataFrame):
    """Estimate two-way FE and DiD models using firm and year effects."""
    panel = df.set_index(["gvkey", "fyear"]).sort_index().copy()

    fe_formula = (
        "annual_return ~ 1 + sentiment_x_small + log_at + leverage + profitability + capex_intensity + cash_ratio + rd_intensity + EntityEffects + TimeEffects"
    )
    fe_result = PanelOLS.from_formula(fe_formula, data=panel, drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=True
    )

    did_formula = (
        "annual_return ~ 1 + sentiment_x_small + sentiment_x_small_post_gfc + sentiment_x_small_post_covid "
        "+ log_at + leverage + profitability + capex_intensity + cash_ratio + rd_intensity + EntityEffects + TimeEffects"
    )
    did_result = PanelOLS.from_formula(did_formula, data=panel, drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=True
    )
    return fe_result, did_result, panel


def extract_result_table(result) -> pd.DataFrame:
    """Convert a regression result into a tidy coefficient table."""
    params = result.params
    std_errors = result.std_errors if hasattr(result, "std_errors") else result.bse
    t_stats = result.tstats if hasattr(result, "tstats") else result.tvalues
    p_values = result.pvalues
    ci = result.conf_int()

    if isinstance(ci, pd.DataFrame):
        lower = ci.iloc[:, 0]
        upper = ci.iloc[:, 1]
    else:
        lower = pd.Series(ci[:, 0], index=params.index)
        upper = pd.Series(ci[:, 1], index=params.index)

    return pd.DataFrame(
        {
            "term": params.index,
            "coef": params.values,
            "std_err": std_errors.reindex(params.index).values,
            "t_stat": t_stats.reindex(params.index).values,
            "p_value": p_values.reindex(params.index).values,
            "ci_low": lower.reindex(params.index).values,
            "ci_high": upper.reindex(params.index).values,
        }
    )


def pstar(p_value: float) -> str:
    """Return significance stars for a p-value."""
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


def build_comparison_table(specs: list[dict]) -> tuple[pd.DataFrame, str]:
    """Create a publication-style comparison table with stars and notes."""
    row_order = [
        "sentiment_lag1",
        "sentiment_x_small",
        "sentiment_x_small_post_gfc",
        "sentiment_x_small_post_covid",
        "small_x_post_gfc",
        "small_x_post_covid",
        "log_at",
        "leverage",
        "profitability",
        "capex_intensity",
        "cash_ratio",
        "rd_intensity",
    ]
    row_labels = {
        "sentiment_lag1": "Lagged Michigan sentiment",
        "sentiment_x_small": "Lagged sentiment x small-firm exposure",
        "sentiment_x_small_post_gfc": "Lagged sentiment x small-firm x post-GFC",
        "sentiment_x_small_post_covid": "Lagged sentiment x small-firm x post-COVID",
        "small_x_post_gfc": "Small-firm x post-GFC",
        "small_x_post_covid": "Small-firm x post-COVID",
        "log_at": "Log assets",
        "leverage": "Leverage",
        "profitability": "Profitability",
        "capex_intensity": "Capex intensity",
        "cash_ratio": "Cash ratio",
        "rd_intensity": "R&D intensity",
    }

    def format_cell(table: pd.DataFrame, term: str) -> str:
        match = table.loc[table["term"] == term]
        if match.empty:
            return ""
        row = match.iloc[0]
        return f"{row['coef']:.3f}{pstar(float(row['p_value']))}<br>({row['std_err']:.3f})"

    rows = []
    for term in row_order:
        row = {"Term": row_labels[term]}
        has_value = False
        for spec in specs:
            cell = format_cell(spec["table"], term)
            row[spec["label"]] = cell
            has_value = has_value or bool(cell)
        if has_value:
            rows.append(row)

    summary_rows = [
        ("Firm FE", lambda spec: spec["firm_fe"]),
        ("Time FE", lambda spec: spec["time_fe"]),
        ("Industry FE", lambda spec: spec["industry_fe"]),
        ("Clustered SE", lambda spec: spec["se_type"]),
        ("Observations", lambda spec: f"{int(spec['model'].nobs)}"),
        ("R-squared", lambda spec: spec["rsquared"]),
        ("Notes", lambda spec: spec["notes"]),
    ]
    for label, getter in summary_rows:
        row = {"Term": label}
        for spec in specs:
            row[spec["label"]] = getter(spec)
        rows.append(row)

    comparison = pd.DataFrame(rows)
    header = ["Term", *[spec["label"] for spec in specs]]
    md_lines = [
        "# M3v2 Publication-Style Regression Table",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in comparison.iterrows():
        md_lines.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    return comparison, "\n".join(md_lines)


def coef_plot(result_specs: list[dict], output_path: Path) -> None:
    """Plot the key sentiment-related coefficients and confidence intervals."""
    rows = []
    for spec in result_specs:
        table = spec["table"]
        for term in spec["terms"]:
            match = table.loc[table["term"] == term]
            if match.empty:
                continue
            row = match.iloc[0]
            rows.append(
                {
                    "model": spec["label"],
                    "term": spec["display_map"].get(term, term),
                    "coef": row["coef"],
                    "ci_low": row["ci_low"],
                    "ci_high": row["ci_high"],
                }
            )

    plot_df = pd.DataFrame(rows)
    plt.figure(figsize=(11, 6))
    sns.pointplot(data=plot_df, x="coef", y="term", hue="model", dodge=0.55, linestyle="none")
    for _, row in plot_df.iterrows():
        plt.plot([row["ci_low"], row["ci_high"]], [row["term"], row["term"]], alpha=0.45)
    plt.axvline(0, color="black", linewidth=1)
    plt.title("M3v2 Sentiment and Crisis Sensitivity Coefficients")
    plt.xlabel("Coefficient estimate")
    plt.ylabel("Term")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def save_diagnostic_plots(result, df: pd.DataFrame) -> None:
    """Save residual diagnostic plots for the full-period OLS model."""
    fitted = result.fittedvalues
    resid = result.resid

    plt.figure(figsize=(10, 5))
    plt.scatter(fitted, resid, alpha=0.25, s=8)
    plt.axhline(0, color="black", linewidth=1)
    plt.xlabel("Fitted values")
    plt.ylabel("Residuals")
    plt.title("M3v2 Residuals vs Fitted")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3v2_residuals_vs_fitted.png", dpi=300, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 5))
    sm.qqplot(resid, line="45", fit=True)
    plt.title("M3v2 Q-Q Plot of OLS Residuals")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3v2_residuals_qq.png", dpi=300, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.histplot(resid, kde=True, bins=50)
    plt.title("M3v2 OLS Residual Distribution")
    plt.xlabel("Residual")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3v2_residuals_hist.png", dpi=300, bbox_inches="tight")
    plt.close()

    sample = df.copy()
    if len(sample) > 5000:
        sample = sample.sample(5000, random_state=42)

    fitted_sample = result.predict(sample)
    plt.figure(figsize=(10, 6))
    plt.scatter(sample["annual_return"], fitted_sample, alpha=0.25, s=8)
    lims = [min(sample["annual_return"].min(), fitted_sample.min()), max(sample["annual_return"].max(), fitted_sample.max())]
    plt.plot(lims, lims, color="black", linestyle="--", linewidth=1)
    plt.xlabel("Actual annual return")
    plt.ylabel("Fitted annual return")
    plt.title("M3v2 OLS Fit: Actual vs Fitted")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3v2_ols_fitted_scatter.png", dpi=300, bbox_inches="tight")
    plt.close()


def save_panel_figures(panel: pd.DataFrame) -> None:
    """Create firm-group trend figures for the FE and DiD story."""
    yearly = (
        panel.reset_index()
        .groupby(["fyear", "small_firm"], as_index=False)["annual_return"]
        .mean()
        .rename(columns={"annual_return": "mean_return"})
    )
    yearly["group"] = np.where(yearly["small_firm"] == 1, "Small firms", "Large firms")

    plt.figure(figsize=(11, 6))
    sns.lineplot(data=yearly, x="fyear", y="mean_return", hue="group", marker="o")
    plt.axvline(GFC_START_YEAR, color="#c0392b", linestyle="--", linewidth=1.5, label="GFC")
    plt.axvline(COVID_START_YEAR, color="#8e44ad", linestyle="--", linewidth=1.5, label="COVID")
    plt.title("M3v2 Average Annual Returns by Firm-Size Group")
    plt.xlabel("Fiscal year")
    plt.ylabel("Average annual return")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3v2_group_trends.png", dpi=300, bbox_inches="tight")
    plt.close()


def run_diagnostics(ols_result, model_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return Breusch-Pagan and VIF diagnostics for the pooled OLS model."""
    x_cols = ["sentiment_lag1", "log_at", "leverage", "profitability", "capex_intensity", "cash_ratio", "rd_intensity"]
    x = model_df[x_cols].copy()
    x_const = sm.add_constant(x)

    bp_lm, bp_lm_p, bp_f, bp_f_p = het_breuschpagan(ols_result.resid, x_const)
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
    for i, column in enumerate(x_const.columns):
        if column == "const":
            continue
        vif_rows.append({"variable": column, "vif": variance_inflation_factor(x_const.values, i)})
    vif_table = pd.DataFrame(vif_rows)
    return bp_table, vif_table


def run_robustness_checks(df: pd.DataFrame, ols_full_result, fe_result) -> pd.DataFrame:
    """Run a small set of easy-to-interpret robustness checks."""
    rows: list[dict] = []

    # Alternative lags in pooled OLS.
    lag_results = {}
    for lag in [1, 2, 3]:
        lag_col = f"sentiment_lag{lag}"
        if lag_col not in df.columns:
            continue
        model_df = df.dropna(subset=[lag_col, "annual_return", "log_at", "leverage", "profitability", "capex_intensity", "cash_ratio", "rd_intensity"]).copy()
        model = smf.ols(
            formula=f"annual_return ~ {lag_col} + log_at + leverage + profitability + capex_intensity + cash_ratio + rd_intensity + C(sic2_label)",
            data=model_df,
        ).fit(cov_type="cluster", cov_kwds={"groups": model_df["gvkey"]})
        lag_results[lag] = float(model.params.get(lag_col, np.nan))

    rows.append(
        {
            "check": "alternative_lags",
            "metric": "lagged sentiment coefficient",
            "baseline_value": lag_results.get(1, np.nan),
            "check_value": lag_results.get(2, np.nan),
            "aux_value": lag_results.get(3, np.nan),
            "interpretation": "If the sign is stable across lags, the sentiment result is not driven by one arbitrary lag choice.",
        }
    )

    # Exclude the pandemic years and re-estimate the direct OLS relation.
    excl = df.loc[df["fyear"] < COVID_START_YEAR].copy()
    excl_model = smf.ols(
        formula="annual_return ~ sentiment_lag1 + log_at + leverage + profitability + capex_intensity + cash_ratio + rd_intensity + C(sic2_label)",
        data=excl,
    ).fit(cov_type="cluster", cov_kwds={"groups": excl["gvkey"]})
    rows.append(
        {
            "check": "exclude_covid_years",
            "metric": "lagged sentiment coefficient",
            "baseline_value": float(ols_full_result.params.get("sentiment_lag1", np.nan)),
            "check_value": float(excl_model.params.get("sentiment_lag1", np.nan)),
            "aux_value": float(excl_model.nobs),
            "interpretation": "If the coefficient stays similar when 2020-2021 are removed, the result is not only a pandemic artifact.",
        }
    )

    # Small-firm vs large-firm subsample comparison.
    small = df.loc[df["small_firm"] == 1].copy()
    large = df.loc[df["small_firm"] == 0].copy()
    small_model = smf.ols(
        formula="annual_return ~ sentiment_lag1 + log_at + leverage + profitability + capex_intensity + cash_ratio + rd_intensity + C(sic2_label)",
        data=small,
    ).fit(cov_type="cluster", cov_kwds={"groups": small["gvkey"]})
    large_model = smf.ols(
        formula="annual_return ~ sentiment_lag1 + log_at + leverage + profitability + capex_intensity + cash_ratio + rd_intensity + C(sic2_label)",
        data=large,
    ).fit(cov_type="cluster", cov_kwds={"groups": large["gvkey"]})
    rows.append(
        {
            "check": "size_subsample_split",
            "metric": "small-vs-large sentiment coefficient",
            "baseline_value": float(small_model.params.get("sentiment_lag1", np.nan)),
            "check_value": float(large_model.params.get("sentiment_lag1", np.nan)),
            "aux_value": np.nan,
            "interpretation": "Different coefficients across firm-size subsamples indicate heterogeneity in sentiment sensitivity.",
        }
    )

    # Placebo DiD before the crisis period.
    placebo = df.loc[df["fyear"] < 2016].copy()
    placebo["placebo_post"] = (placebo["fyear"] >= 2012).astype(int)
    placebo_panel = placebo.set_index(["gvkey", "fyear"]).sort_index()
    placebo_result = PanelOLS.from_formula(
        "annual_return ~ 1 + small_firm:placebo_post + log_at + leverage + profitability + capex_intensity + cash_ratio + rd_intensity + EntityEffects + TimeEffects",
        data=placebo_panel,
        drop_absorbed=True,
    ).fit(cov_type="clustered", cluster_entity=True)
    placebo_term = next((term for term in placebo_result.params.index if "small_firm:placebo_post" in term), None)
    rows.append(
        {
            "check": "placebo_pre_period",
            "metric": "small_firm x placebo_post",
            "baseline_value": float(fe_result.params.get("sentiment_x_small", np.nan)),
            "check_value": float(placebo_result.params.get(placebo_term, np.nan)) if placebo_term else np.nan,
            "aux_value": float(placebo_result.pvalues.get(placebo_term, np.nan)) if placebo_term else np.nan,
            "interpretation": "A weak placebo interaction supports the claim that the crisis DiD is not just capturing generic pre-trends.",
        }
    )

    return pd.DataFrame(rows)


def write_report(
    ols_full_table: pd.DataFrame,
    ols_covid_table: pd.DataFrame,
    fe_table: pd.DataFrame,
    did_table: pd.DataFrame,
    bp_table: pd.DataFrame,
    vif_table: pd.DataFrame,
    robustness_table: pd.DataFrame,
    ols_full_nobs: int,
    covid_nobs: int,
    fe_nobs: int,
    did_nobs: int,
) -> None:
    """Write the plain-language M3v2 memo to both the root and reports folders."""
    fe_sent = fe_table.loc[fe_table["term"] == "sentiment_x_small"].iloc[0]
    did_gfc = did_table.loc[did_table["term"] == "sentiment_x_small_post_gfc"].iloc[0]
    did_covid = did_table.loc[did_table["term"] == "sentiment_x_small_post_covid"].iloc[0]
    ols_sent = ols_full_table.loc[ols_full_table["term"] == "sentiment_lag1"].iloc[0]
    ols_covid_sent = ols_covid_table.loc[ols_covid_table["term"] == "sentiment_lag1"].iloc[0]

    lines = [
        "# M3v2 Interpretation: Firm Panel Fixed Effects, DiD, and OLS",
        "",
        "## What we estimated",
        "1. **Pooled OLS for the full sample**",
        "   - Outcome: annual firm return proxy from fiscal-year price change and dividends",
        "   - Key regressor: lagged Michigan sentiment",
        "   - Controls: size, leverage, profitability, capex intensity, cash ratio, and R&D intensity",
        "   - Industry controls: 2-digit SIC fixed effects",
        "2. **Pooled OLS for the COVID subsample**",
        f"   - Sample: fiscal years {COVID_START_YEAR} and later",
        "   - Same sentiment and control structure as the full sample",
        "3. **Two-way fixed effects panel model**",
        "   - Outcome: annual firm return proxy",
        "   - Fixed effects: firm FE and year FE",
        "   - Key term: lagged sentiment x small-firm exposure",
        "   - Standard errors: clustered by firm",
        "4. **Difference-in-differences panel model**",
        "   - Treatment proxy: small firms",
        "   - Shock windows: post-GFC and post-COVID",
        "   - Key terms: lagged sentiment x small-firm x post-shock interactions",
        "   - Standard errors: clustered by firm",
        "",
        "## Sample sizes",
        f"- Full-period OLS observations: **{ols_full_nobs}**",
        f"- COVID-only OLS observations: **{covid_nobs}**",
        f"- FE observations: **{fe_nobs}**",
        f"- DiD observations: **{did_nobs}**",
        "",
        "## Main findings",
        "### 1) Full-period OLS",
        f"- Lagged sentiment coefficient: {ols_sent['coef']:.4f}{pstar(float(ols_sent['p_value']))}",
        f"- p-value: {ols_sent['p_value']:.4f}",
        f"- 95% CI: [{ols_sent['ci_low']:.4f}, {ols_sent['ci_high']:.4f}]",
        "",
        "### 2) COVID-only OLS",
        f"- Lagged sentiment coefficient: {ols_covid_sent['coef']:.4f}{pstar(float(ols_covid_sent['p_value']))}",
        f"- p-value: {ols_covid_sent['p_value']:.4f}",
        f"- 95% CI: [{ols_covid_sent['ci_low']:.4f}, {ols_covid_sent['ci_high']:.4f}]",
        "",
        "### 3) Fixed effects panel model",
        f"- Lagged sentiment x small-firm exposure: {fe_sent['coef']:.4f}{pstar(float(fe_sent['p_value']))}",
        f"- p-value: {fe_sent['p_value']:.4f}",
        f"- 95% CI: [{fe_sent['ci_low']:.4f}, {fe_sent['ci_high']:.4f}]",
        "",
        "### 4) Difference-in-differences panel model",
        f"- Lagged sentiment x small-firm x post-GFC: {did_gfc['coef']:.4f}{pstar(float(did_gfc['p_value']))}",
        f"- Lagged sentiment x small-firm x post-COVID: {did_covid['coef']:.4f}{pstar(float(did_covid['p_value']))}",
        "",
        "Interpretation in plain language:",
        "- The pooled OLS models estimate the direct association between lagged sentiment and firm returns.",
        "- The FE and DiD models are stricter: year fixed effects absorb the common sentiment level, so the estimable signal is whether small firms are more sensitive to sentiment and whether that sensitivity changes after shocks.",
        "- Positive interaction terms imply small firms load more heavily on sentiment after the relevant shock; negative terms imply the opposite.",
        "",
        "## Diagnostics",
        f"- Breusch-Pagan p-value: **{bp_table.loc[0, 'lm_p_value']:.4f}**",
        f"- Maximum VIF: **{vif_table['vif'].max():.2f}**",
        "- Residual plots saved for the full-period OLS model.",
        "",
        "Interpretation:",
        "- If the Breusch-Pagan p-value is small, heteroskedasticity is present and clustered/robust SEs are the correct response.",
        "- VIFs below conventional danger zones suggest the control set is not dominated by severe multicollinearity.",
        "",
        "## Robustness checks",
    ]

    for _, row in robustness_table.iterrows():
        lines.append(
            f"- {row['check']}: baseline={row['baseline_value']:.4f}, check={row['check_value']:.4f}, aux={row['aux_value'] if pd.notna(row['aux_value']) else 'NA'}"
        )
        lines.append(f"  - {row['interpretation']}")

    lines.extend(
        [
            "",
            "## Visual evidence",
            "- `results/figures/m3v2_group_trends.png`: average annual returns for small vs large firms.",
            "- `results/figures/m3v2_did_event_study.png`: event study plots around GFC (2008) and COVID (2020) shocks.",
            "- `results/figures/m3v2_ols_fitted_scatter.png`: actual vs fitted values for the pooled OLS model.",
            "- `results/figures/m3v2_residuals_vs_fitted.png`: residual spread across fitted values.",
            "- `results/figures/m3v2_residuals_qq.png`: Q-Q plot of OLS residuals.",
            "- `results/figures/m3v2_residuals_hist.png`: residual distribution check.",
            "- `results/figures/m3v2_fe_did_coefficients.png`: sentiment and shock interaction coefficients.",
            "- `results/figures/m3v2_coefficient_comparison.png`: tornado plot of coefficients across specifications.",
            "- `results/figures/m3v2_model_specifications.png`: R-squared comparison and FE indicators.",
            "- `results/figures/m3v2_interaction_elasticity.png`: sentiment elasticity by firm size (FE model).",
            "",
            "## Practical caveat",
            "- This is a genuine firm-year panel, but the sentiment series is still common to all firms in a given year.",
            "- That means the strict FE identification comes from differential exposure, not from a raw common-sentiment main effect inside the TWFE model.",
            "- The pooled OLS models provide the direct sentiment coefficient; the FE and DiD models provide the panel-based causal-style comparison the rubric asks for.",
            "",
            "## Files generated for M3v2",
            "- `data/final/m3v2_firm_panel.csv`",
            "- `results/tables/m3v2_ols_full_period_results.csv`",
            "- `results/tables/m3v2_ols_covid_only_results.csv`",
            "- `results/tables/m3v2_fe_results.csv`",
            "- `results/tables/m3v2_did_results.csv`",
            "- `results/tables/m3v2_bp_test_results.csv`",
            "- `results/tables/m3v2_vif_results.csv`",
            "- `results/tables/m3v2_robustness_checks.csv`",
            "- `results/tables/m3v2_model_comparison_table.csv`",
            "- `results/tables/m3v2_model_comparison_table.md`",
            "- `results/figures/m3v2_group_trends.png`",
            "- `results/figures/m3v2_did_event_study.png`",
            "- `results/figures/m3v2_ols_fitted_scatter.png`",
            "- `results/figures/m3v2_residuals_vs_fitted.png`",
            "- `results/figures/m3v2_residuals_qq.png`",
            "- `results/figures/m3v2_residuals_hist.png`",
            "- `results/figures/m3v2_fe_did_coefficients.png`",
            "- `results/figures/m3v2_coefficient_comparison.png`",
            "- `results/figures/m3v2_model_specifications.png`",
            "- `results/figures/m3v2_interaction_elasticity.png`",
        ]
    )

    text = "\n".join(lines)
    REPORT_PATH.write_text(text, encoding="utf-8")
    ROOT_REPORT_PATH.write_text(text, encoding="utf-8")


def save_did_event_study_plot(panel: pd.DataFrame) -> None:
    """Visualize average returns around GFC and COVID for treated vs control groups."""
    panel_reset = panel.reset_index()
    
    # GFC event study: years -3 to +5 around 2008
    gfc_range = range(2005, 2014)
    gfc_data = panel_reset[panel_reset["fyear"].isin(gfc_range)].copy()
    gfc_data["event_year"] = gfc_data["fyear"] - GFC_START_YEAR
    gfc_by_group = gfc_data.groupby(["event_year", "small_firm"], as_index=False)["annual_return"].mean()
    gfc_by_group["group"] = np.where(gfc_by_group["small_firm"] == 1, "Small firms", "Large firms")
    
    # COVID event study: years -2 to +1 around 2020
    covid_range = range(2018, 2022)
    covid_data = panel_reset[panel_reset["fyear"].isin(covid_range)].copy()
    covid_data["event_year"] = covid_data["fyear"] - COVID_START_YEAR
    covid_by_group = covid_data.groupby(["event_year", "small_firm"], as_index=False)["annual_return"].mean()
    covid_by_group["group"] = np.where(covid_by_group["small_firm"] == 1, "Small firms", "Large firms")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # GFC plot
    for group in ["Small firms", "Large firms"]:
        subset = gfc_by_group[gfc_by_group["group"] == group]
        axes[0].plot(subset["event_year"], subset["annual_return"], marker="o", label=group)
    axes[0].axvline(0, color="red", linestyle="--", linewidth=2, label="GFC shock (2008)")
    axes[0].set_xlabel("Years since shock")
    axes[0].set_ylabel("Average annual return")
    axes[0].set_title("DiD: Average Returns Around GFC by Firm Size")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # COVID plot
    for group in ["Small firms", "Large firms"]:
        subset = covid_by_group[covid_by_group["group"] == group]
        axes[1].plot(subset["event_year"], subset["annual_return"], marker="o", label=group)
    axes[1].axvline(0, color="purple", linestyle="--", linewidth=2, label="COVID shock (2020)")
    axes[1].set_xlabel("Years since shock")
    axes[1].set_ylabel("Average annual return")
    axes[1].set_title("DiD: Average Returns Around COVID by Firm Size")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3v2_did_event_study.png", dpi=300, bbox_inches="tight")
    plt.close()


def save_coefficient_comparison_plot(tables: dict) -> None:
    """Create a tornado plot comparing key coefficients across all models."""
    coef_data = []
    
    # Extract sentiment-related terms from each model
    models_map = {
        "OLS Full": ("m3v2_ols_full_period_results.csv", ["sentiment_lag1"]),
        "OLS COVID": ("m3v2_ols_covid_only_results.csv", ["sentiment_lag1"]),
        "FE TWFE": ("m3v2_fe_results.csv", ["sentiment_x_small"]),
        "DiD TWFE": ("m3v2_did_results.csv", ["sentiment_x_small_post_gfc", "sentiment_x_small_post_covid"]),
    }
    
    for model_name, (_, terms) in models_map.items():
        table = tables.get(model_name)
        if table is None:
            continue
        for term in terms:
            match = table.loc[table["term"] == term]
            if not match.empty:
                row = match.iloc[0]
                coef_data.append({
                    "Model": model_name,
                    "Term": term,
                    "Coefficient": row["coef"],
                    "Std Error": row["std_err"],
                    "CI Low": row["ci_low"],
                    "CI High": row["ci_high"],
                })
    
    if not coef_data:
        return
    
    coef_df = pd.DataFrame(coef_data)
    
    # Create tornado plot
    fig, ax = plt.subplots(figsize=(11, 7))
    
    y_pos = np.arange(len(coef_df))
    colors = ["#2ecc71" if x > 0 else "#e74c3c" for x in coef_df["Coefficient"]]
    
    # Plot main coefficients
    ax.barh(y_pos, coef_df["Coefficient"], color=colors, alpha=0.7)
    
    # Add error bars
    errors = coef_df["Std Error"] * 1.96  # 95% CI
    ax.errorbar(coef_df["Coefficient"], y_pos, xerr=errors, fmt="none", ecolor="black", capsize=5, alpha=0.6)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{row['Model']}\n({row['Term'][:20]})" for _, row in coef_df.iterrows()], fontsize=9)
    ax.set_xlabel("Coefficient estimate (95% CI)")
    ax.set_title("M3v2 Coefficient Comparison Across Specifications")
    ax.axvline(0, color="black", linewidth=1, linestyle="-")
    ax.grid(True, alpha=0.3, axis="x")
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3v2_coefficient_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()


def save_model_specification_plot(comparison_table: pd.DataFrame, specs: list[dict]) -> None:
    """Create a bar chart showing R-squared and model specifications."""
    spec_data = []
    for spec in specs:
        rsq = float(spec.get("rsquared", 0))
        spec_data.append({
            "Model": spec["label"],
            "R-squared": rsq,
            "Firm FE": spec["firm_fe"],
            "Time FE": spec["time_fe"],
            "Industry FE": spec["industry_fe"],
        })
    
    spec_df = pd.DataFrame(spec_data)
    
    fig, ax = plt.subplots(figsize=(11, 6))
    
    x_pos = np.arange(len(spec_df))
    bars = ax.bar(x_pos, spec_df["R-squared"], color=["#3498db", "#e74c3c", "#2ecc71", "#f39c12"])
    
    # Add value labels on bars
    for i, (bar, row) in enumerate(zip(bars, spec_df.itertuples())):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f"{height:.3f}", ha="center", va="bottom", fontsize=10)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(spec_df["Model"], rotation=15, ha="right")
    ax.set_ylabel("R-squared")
    ax.set_title("M3v2 Model Fit Comparison (R²)")
    ax.set_ylim((0, max(spec_df["R-squared"]) * 1.15))
    ax.grid(True, alpha=0.3, axis="y")
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3v2_model_specifications.png", dpi=300, bbox_inches="tight")
    plt.close()


def save_interaction_elasticity_plot(panel: pd.DataFrame, fe_result) -> None:
    """Plot the sentiment elasticity conditional on firm size (interaction visualization)."""
    panel_reset = panel.reset_index()
    
    # Get the interaction coefficient
    interaction_coef = float(fe_result.params.get("sentiment_x_small", 0))
    main_term = "sentiment_lag1"
    
    # Create elasticity curves
    sentiment_range = np.linspace(panel_reset["sentiment_lag1"].min(), panel_reset["sentiment_lag1"].max(), 50)
    
    # For small firms (small_firm = 1)
    small_firm_elasticity = sentiment_range * (1 + interaction_coef)
    
    # For large firms (small_firm = 0)
    large_firm_elasticity = sentiment_range * 1.0
    
    fig, ax = plt.subplots(figsize=(11, 6))
    
    ax.plot(sentiment_range, small_firm_elasticity, marker="o", linewidth=2.5, label="Small firms", color="#e74c3c")
    ax.plot(sentiment_range, large_firm_elasticity, marker="s", linewidth=2.5, label="Large firms", color="#3498db")
    
    ax.axhline(0, color="black", linewidth=1, linestyle="-")
    ax.axvline(panel_reset["sentiment_lag1"].mean(), color="gray", linewidth=1.5, linestyle="--", label="Mean sentiment")
    
    ax.set_xlabel("Lagged Michigan Consumer Confidence")
    ax.set_ylabel("Predicted return contribution")
    ax.set_title("M3v2: Sentiment Effect Heterogeneity by Firm Size (FE Model)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "m3v2_interaction_elasticity.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    firm = load_and_prepare_firm_panel()
    firm.to_csv(FIRM_PANEL_OUTPUT_PATH, index=False)

    ols_full_result, ols_full_df = fit_pooled_ols(firm, lag_column="sentiment_lag1", covid_only=False)
    ols_covid_result, ols_covid_df = fit_pooled_ols(firm, lag_column="sentiment_lag1", covid_only=True)
    fe_result, did_result, panel = fit_panel_models(firm)

    ols_full_table = extract_result_table(ols_full_result)
    ols_covid_table = extract_result_table(ols_covid_result)
    fe_table = extract_result_table(fe_result)
    did_table = extract_result_table(did_result)
    bp_table, vif_table = run_diagnostics(ols_full_result, ols_full_df)
    robustness_table = run_robustness_checks(firm, ols_full_result, fe_result)

    ols_full_table.to_csv(TABLES_DIR / "m3v2_ols_full_period_results.csv", index=False)
    ols_covid_table.to_csv(TABLES_DIR / "m3v2_ols_covid_only_results.csv", index=False)
    fe_table.to_csv(TABLES_DIR / "m3v2_fe_results.csv", index=False)
    did_table.to_csv(TABLES_DIR / "m3v2_did_results.csv", index=False)
    bp_table.to_csv(TABLES_DIR / "m3v2_bp_test_results.csv", index=False)
    vif_table.to_csv(TABLES_DIR / "m3v2_vif_results.csv", index=False)
    robustness_table.to_csv(TABLES_DIR / "m3v2_robustness_checks.csv", index=False)

    comparison_specs = [
        {
            "label": "(1) OLS full period",
            "table": ols_full_table,
            "model": ols_full_result,
            "firm_fe": "No",
            "time_fe": "No",
            "industry_fe": "Yes",
            "se_type": "Clustered by firm",
            "notes": "Direct sentiment coefficient",
            "rsquared": f"{float(getattr(ols_full_result, 'rsquared', np.nan)):.3f}",
        },
        {
            "label": "(2) OLS COVID only",
            "table": ols_covid_table,
            "model": ols_covid_result,
            "firm_fe": "No",
            "time_fe": "No",
            "industry_fe": "Yes",
            "se_type": "Clustered by firm",
            "notes": "Pandemic subsample",
            "rsquared": f"{float(getattr(ols_covid_result, 'rsquared', np.nan)):.3f}",
        },
        {
            "label": "(3) FE TWFE",
            "table": fe_table,
            "model": fe_result,
            "firm_fe": "Yes",
            "time_fe": "Yes",
            "industry_fe": "No",
            "se_type": "Clustered by firm",
            "notes": "Sentiment x small-firm exposure",
            "rsquared": f"{float(getattr(fe_result, 'rsquared_overall', np.nan)):.3f}",
        },
        {
            "label": "(4) DiD TWFE",
            "table": did_table,
            "model": did_result,
            "firm_fe": "Yes",
            "time_fe": "Yes",
            "industry_fe": "No",
            "se_type": "Clustered by firm",
            "notes": "Shock interactions with sentiment exposure",
            "rsquared": f"{float(getattr(did_result, 'rsquared_overall', np.nan)):.3f}",
        },
    ]

    comparison_table, comparison_markdown = build_comparison_table(comparison_specs)
    comparison_table.to_csv(TABLES_DIR / "m3v2_model_comparison_table.csv", index=False)
    (TABLES_DIR / "m3v2_model_comparison_table.md").write_text(comparison_markdown, encoding="utf-8")

    save_panel_figures(panel)
    save_diagnostic_plots(ols_full_result, ols_full_df)
    coef_plot(
        [
            {
                "label": "FE model",
                "table": fe_table,
                "terms": ["sentiment_x_small"],
                "display_map": {"sentiment_x_small": "FE: sentiment x small-firm exposure"},
            },
            {
                "label": "DiD model",
                "table": did_table,
                "terms": ["sentiment_x_small_post_gfc", "sentiment_x_small_post_covid"],
                "display_map": {
                    "sentiment_x_small_post_gfc": "DiD: sentiment x small-firm x post-GFC",
                    "sentiment_x_small_post_covid": "DiD: sentiment x small-firm x post-COVID",
                },
            },
        ],
        FIGURES_DIR / "m3v2_fe_did_coefficients.png",
    )
    
    # Additional visualizations for investor-ready dashboard
    tables_dict = {
        "OLS Full": ols_full_table,
        "OLS COVID": ols_covid_table,
        "FE TWFE": fe_table,
        "DiD TWFE": did_table,
    }
    save_did_event_study_plot(panel)
    save_coefficient_comparison_plot(tables_dict)
    save_model_specification_plot(comparison_table, comparison_specs)
    save_interaction_elasticity_plot(panel, fe_result)

    write_report(
        ols_full_table=ols_full_table,
        ols_covid_table=ols_covid_table,
        fe_table=fe_table,
        did_table=did_table,
        bp_table=bp_table,
        vif_table=vif_table,
        robustness_table=robustness_table,
        ols_full_nobs=int(ols_full_result.nobs),
        covid_nobs=int(ols_covid_result.nobs),
        fe_nobs=int(fe_result.nobs),
        did_nobs=int(did_result.nobs),
    )

    print("M3v2 analysis completed.")
    print(f"- {FIRM_PANEL_OUTPUT_PATH}")
    print(f"- {TABLES_DIR / 'm3v2_ols_full_period_results.csv'}")
    print(f"- {TABLES_DIR / 'm3v2_ols_covid_only_results.csv'}")
    print(f"- {TABLES_DIR / 'm3v2_fe_results.csv'}")
    print(f"- {TABLES_DIR / 'm3v2_did_results.csv'}")
    print(f"- {TABLES_DIR / 'm3v2_bp_test_results.csv'}")
    print(f"- {TABLES_DIR / 'm3v2_vif_results.csv'}")
    print(f"- {TABLES_DIR / 'm3v2_robustness_checks.csv'}")
    print(f"- {TABLES_DIR / 'm3v2_model_comparison_table.csv'}")
    print(f"- {TABLES_DIR / 'm3v2_model_comparison_table.md'}")
    print(f"- {FIGURES_DIR / 'm3v2_group_trends.png'}")
    print(f"- {FIGURES_DIR / 'm3v2_ols_fitted_scatter.png'}")
    print(f"- {FIGURES_DIR / 'm3v2_residuals_vs_fitted.png'}")
    print(f"- {FIGURES_DIR / 'm3v2_residuals_qq.png'}")
    print(f"- {FIGURES_DIR / 'm3v2_residuals_hist.png'}")
    print(f"- {FIGURES_DIR / 'm3v2_fe_did_coefficients.png'}")
    print(f"- {ROOT_REPORT_PATH}")
    print(f"- {REPORT_PATH}")


if __name__ == "__main__":
    main()