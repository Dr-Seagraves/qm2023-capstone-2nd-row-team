"""Create an investor-ready interactive dashboard for M3v2 analysis.

This dashboard provides:
- Executive summary with key metrics
- Interactive regression comparisons
- Visual evidence of DiD and FE effects
- Model performance metrics
- Downloadable tables and findings

Output:
- results/reports/M3v2_interactive_dashboard.html
"""

from __future__ import annotations

import base64
from pathlib import Path

import importlib
import numpy as np
import pandas as pd

from config_paths import FINAL_DATA_DIR, REPORTS_DIR, TABLES_DIR, FIGURES_DIR

go = importlib.import_module("plotly.graph_objects")
make_subplots = importlib.import_module("plotly.subplots").make_subplots

DASHBOARD_PATH = REPORTS_DIR / "M3v2_interactive_dashboard.html"


def encode_image_as_data_uri(image_path: Path) -> str:
    """Return a PNG image as a base64 data URI for reliable HTML embedding."""
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def load_results() -> dict:
    """Load all M3v2 results tables."""
    results = {}
    
    # Load regression tables
    results["ols_full"] = pd.read_csv(TABLES_DIR / "m3v2_ols_full_period_results.csv")
    results["ols_covid"] = pd.read_csv(TABLES_DIR / "m3v2_ols_covid_only_results.csv")
    results["fe"] = pd.read_csv(TABLES_DIR / "m3v2_fe_results.csv")
    results["did"] = pd.read_csv(TABLES_DIR / "m3v2_did_results.csv")
    results["comparison"] = pd.read_csv(TABLES_DIR / "m3v2_model_comparison_table.csv")
    results["company_comparison"] = pd.read_csv(TABLES_DIR / "m3v2_company_model_comparison_table.csv")
    results["robustness"] = pd.read_csv(TABLES_DIR / "m3v2_robustness_checks.csv")
    results["bp_test"] = pd.read_csv(TABLES_DIR / "m3v2_bp_test_results.csv")
    results["vif"] = pd.read_csv(TABLES_DIR / "m3v2_vif_results.csv")
    results["firm_panel"] = pd.read_csv(FINAL_DATA_DIR / "m3v2_firm_panel.csv")
    
    return results


def create_key_metrics_section() -> str:
    """Create HTML section with key metrics."""
    results = load_results()
    
    # Extract key findings
    ols_full = results["ols_full"]
    fe = results["fe"]
    did = results["did"]
    panel = results["firm_panel"]
    
    sentiment_coef_ols = float(ols_full[ols_full["term"] == "sentiment_lag1"]["coef"].values[0] if any(ols_full["term"] == "sentiment_lag1") else 0)
    sentiment_coef_fe = float(fe[fe["term"] == "sentiment_x_small"]["coef"].values[0] if any(fe["term"] == "sentiment_x_small") else 0)
    
    n_firms = panel["gvkey"].nunique()
    n_obs = len(panel)
    n_years = panel["fyear"].max() - panel["fyear"].min() + 1
    
    small_firm_pct = (panel["small_firm"] == 1).sum() / n_obs * 100
    
    html = f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 8px; margin-bottom: 30px;">
        <h2 style="color: white; text-align: center; margin: 0;">M3v2 Firm-Panel Analysis Dashboard</h2>
        <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 10px 0;">
            Exploring the relationship between consumer sentiment and returns using difference-in-differences methodology
        </p>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
        <div style="background: #ecf0f1; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db;">
            <div style="font-size: 14px; color: #7f8c8d; font-weight: bold;">SAMPLE SIZE</div>
            <div style="font-size: 32px; color: #2c3e50; font-weight: bold;">{n_obs:,}</div>
            <div style="font-size: 12px; color: #95a5a6; margin-top: 10px;">
                {n_firms:,} firms over {int(n_years)} years
            </div>
        </div>
        
        <div style="background: #ecf0f1; padding: 20px; border-radius: 8px; border-left: 4px solid #e74c3c;">
            <div style="font-size: 14px; color: #7f8c8d; font-weight: bold;">SENTIMENT EFFECT (OLS)</div>
            <div style="font-size: 32px; color: #2c3e50; font-weight: bold;">{sentiment_coef_ols:.4f}</div>
            <div style="font-size: 12px; color: #95a5a6; margin-top: 10px;">
                Direct coefficient on lagged Michigan sentiment
            </div>
        </div>
        
        <div style="background: #ecf0f1; padding: 20px; border-radius: 8px; border-left: 4px solid #27ae60;">
            <div style="font-size: 14px; color: #7f8c8d; font-weight: bold;">FE INTERACTION</div>
            <div style="font-size: 32px; color: #2c3e50; font-weight: bold;">{sentiment_coef_fe:.4f}</div>
            <div style="font-size: 12px; color: #95a5a6; margin-top: 10px;">
                Sentiment × small-firm exposure (TWFE)
            </div>
        </div>
        
        <div style="background: #ecf0f1; padding: 20px; border-radius: 8px; border-left: 4px solid #f39c12;">
            <div style="font-size: 14px; color: #7f8c8d; font-weight: bold;">SMALL FIRMS</div>
            <div style="font-size: 32px; color: #2c3e50; font-weight: bold;">{small_firm_pct:.1f}%</div>
            <div style="font-size: 12px; color: #95a5a6; margin-top: 10px;">
                Share of firm-years in sample
            </div>
        </div>
    </div>
    """
    
    return html


def create_regression_comparison_table() -> tuple[str, go.Figure]:
    """Create regression comparison figure and HTML table."""
    results = load_results()
    comparison = results["comparison"]
    
    # Create HTML table
    html_table = comparison.to_html(classes="comparison-table", border=0, escape=False, index=False)
    
    # Extract R-squared for visualization
    rsq_data = []
    model_names = ["(1) OLS Full", "(2) OLS COVID", "(3) FE TWFE", "(4) DiD TWFE"]
    for i, row in comparison.iterrows():
        if "rsquared" in str(row):
            try:
                rsq = float(row.get("rsquared", 0)) if row.get("rsquared") else 0
            except:
                rsq = 0
        else:
            rsq = 0
        rsq_data.append({"model": model_names[i] if i < len(model_names) else f"Model {i+1}", "rsq": rsq})
    
    rsq_df = pd.DataFrame(rsq_data)
    
    fig = go.Figure(
        data=[
            go.Bar(
                x=rsq_df["model"],
                y=rsq_df["rsq"],
                marker=dict(color=["#3498db", "#e74c3c", "#2ecc71", "#f39c12"], line=dict(color="white", width=2)),
                text=[f"{v:.3f}" for v in rsq_df["rsq"]],
                textposition="outside",
                showlegend=False,
            )
        ]
    )
    
    fig.update_layout(
        title="Model Fit Comparison (R²)",
        xaxis_title="Specification",
        yaxis_title="R-squared",
        hovermode="x",
        template="plotly_white",
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
    )
    
    return html_table, fig


def create_company_controls_section() -> str:
    """Create HTML for the stepwise company-controls ladder."""
    results = load_results()
    company = results["company_comparison"]
    html_table = company.fillna("").to_html(classes="comparison-table", border=0, escape=False, index=False)
    dashboard_image = encode_image_as_data_uri(FIGURES_DIR / "m3v2_company_regression_dashboard.png")

    return f"""
    <div class="section">
        <h2>Company Controls Ladder</h2>
        <div class="info-box">
            <strong>Why this table matters:</strong> It keeps the same firm-year sample across columns and adds
            controls in an economically sensible order: size, industry, capital structure, sales scale,
            profitability/liquidity, investment intensity, and market valuation.
        </div>
        <div class="figure-section">
            <h3>Stepwise PNG Dashboard</h3>
            <p style="color: #7f8c8d; margin-bottom: 15px;">
                The static dashboard below summarizes the sentiment coefficient and model fit as controls accumulate.
            </p>
            <img src="{dashboard_image}" alt="M3v2 company regression dashboard" style="width: 100%; border-radius: 8px; border: 1px solid #ecf0f1; display: block;" />
        </div>
        <div class="figure-section">
            <h3>Publication-Style Table</h3>
            {html_table}
        </div>
    </div>
    """


def create_coefficient_explorer() -> go.Figure:
    """Create interactive coefficient explorer across models."""
    results = load_results()
    
    ols_full = results["ols_full"]
    ols_covid = results["ols_covid"]
    fe = results["fe"]
    did = results["did"]
    
    # Collect key terms
    coef_data = []
    
    # OLS Full
    for _, row in ols_full.iterrows():
        if row["term"] in ["sentiment_lag1", "log_at", "leverage"]:
            coef_data.append({
                "Model": "OLS Full",
                "Term": row["term"],
                "Coef": row["coef"],
                "SE": row["std_err"],
                "CI Low": row["ci_low"],
                "CI High": row["ci_high"],
                "P-value": row["p_value"],
            })
    
    # FE
    for _, row in fe.iterrows():
        if row["term"] in ["sentiment_x_small", "log_at", "leverage"]:
            coef_data.append({
                "Model": "FE TWFE",
                "Term": row["term"],
                "Coef": row["coef"],
                "SE": row["std_err"],
                "CI Low": row["ci_low"],
                "CI High": row["ci_high"],
                "P-value": row["p_value"],
            })
    
    # DiD
    for _, row in did.iterrows():
        if row["term"] in ["sentiment_x_small_post_gfc", "sentiment_x_small_post_covid"]:
            coef_data.append({
                "Model": "DiD TWFE",
                "Term": row["term"],
                "Coef": row["coef"],
                "SE": row["std_err"],
                "CI Low": row["ci_low"],
                "CI High": row["ci_high"],
                "P-value": row["p_value"],
            })
    
    coef_df = pd.DataFrame(coef_data)
    
    # Create figure
    fig = go.Figure()
    
    models = coef_df["Model"].unique()
    colors = {"OLS Full": "#3498db", "FE TWFE": "#2ecc71", "DiD TWFE": "#f39c12"}
    
    for model in models:
        model_data = coef_df[coef_df["Model"] == model]
        
        fig.add_trace(
            go.Scatter(
                x=model_data["Coef"],
                y=model_data["Term"],
                mode="markers",
                name=model,
                marker=dict(size=10, color=colors.get(model, "#95a5a6")),
                error_x=dict(
                    type="data",
                    array=model_data["SE"] * 1.96,
                    visible=True,
                ),
                text=[
                    f"<b>{model}</b><br>Term: {term}<br>Coef: {coef:.4f}<br>P-val: {pval:.3f}"
                    for term, coef, pval in zip(model_data["Term"], model_data["Coef"], model_data["P-value"])
                ],
                hovertemplate="%{text}<extra></extra>",
            )
        )
    
    fig.add_vline(x=0, line_dash="dash", line_color="gray", annotation_text="No effect", annotation_position="top left")
    
    fig.update_layout(
        title="Coefficient Explorer: Key Terms Across Models",
        xaxis_title="Coefficient Estimate (with 95% CI)",
        yaxis_title="Term",
        hovermode="closest",
        template="plotly_white",
        height=500,
        showlegend=True,
        legend=dict(x=0.02, y=0.98),
    )
    
    return fig


def create_robustness_summary() -> go.Figure:
    """Visualize robustness checks."""
    results = load_results()
    robustness = results["robustness"]
    
    # Prepare data for visualization
    rob_data = []
    for _, row in robustness.iterrows():
        rob_data.append({
            "Check": str(row["check"]),
            "Baseline": float(row["baseline_value"]),
            "Check Value": float(row["check_value"]),
            "Difference": float(row["check_value"]) - float(row["baseline_value"]),
        })
    
    rob_df = pd.DataFrame(rob_data)
    
    fig = go.Figure(
        data=[
            go.Bar(
                name="Baseline",
                x=rob_df["Check"],
                y=rob_df["Baseline"],
                marker=dict(color="#3498db"),
            ),
            go.Bar(
                name="Robustness Check",
                x=rob_df["Check"],
                y=rob_df["Check Value"],
                marker=dict(color="#e74c3c"),
            ),
        ]
    )
    
    fig.update_layout(
        title="Robustness Checks: Baseline vs Alternative Specifications",
        xaxis_title="Check Type",
        yaxis_title="Coefficient Value",
        barmode="group",
        hovermode="x",
        template="plotly_white",
        height=400,
        margin=dict(l=50, r=50, t=50, b=100),
        xaxis_tickangle=-45,
    )
    
    return fig


def create_diagnostic_summary() -> str:
    """Create HTML section summarizing diagnostics."""
    results = load_results()
    bp_test = results["bp_test"]
    vif = results["vif"]
    
    # Breusch-Pagan test
    bp_row = bp_test.iloc[0]
    bp_p = float(bp_row["lm_p_value"])
    bp_interpretation = "No heteroskedasticity detected" if bp_p > 0.05 else "Heteroskedasticity detected"
    
    # VIF stats
    max_vif = float(vif["vif"].max())
    mean_vif = float(vif["vif"].mean())
    
    html = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h3 style="color: #2c3e50; margin-top: 0;">Diagnostic Summary</h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            <div>
                <h4 style="color: #34495e; margin-bottom: 10px;">Breusch-Pagan Test</h4>
                <p style="color: #7f8c8d; margin: 0;">
                    <span style="font-weight: bold;">P-value:</span> {bp_p:.4f}<br>
                    <span style="font-weight: bold;">Result:</span> {bp_interpretation}<br>
                    <span style="color: #95a5a6; font-size: 12px;">
                        Null: homoskedastic errors
                    </span>
                </p>
            </div>
            
            <div>
                <h4 style="color: #34495e; margin-bottom: 10px;">Multicollinearity (VIF)</h4>
                <p style="color: #7f8c8d; margin: 0;">
                    <span style="font-weight: bold;">Max VIF:</span> {max_vif:.2f}<br>
                    <span style="font-weight: bold;">Mean VIF:</span> {mean_vif:.2f}<br>
                    <span style="color: #95a5a6; font-size: 12px;">
                        VIF < 5 indicates low multicollinearity
                    </span>
                </p>
            </div>
        </div>
    </div>
    """
    
    return html


def create_html_dashboard(results_dict: dict, figs_dict: dict) -> str:
    """Assemble complete HTML dashboard."""
    
    # Build the HTML
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>M3v2 Firm-Panel Analysis - Interactive Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px 30px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section h2 {
            color: #2c3e50;
            font-size: 1.8em;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .metric-label {
            font-size: 14px;
            color: #7f8c8d;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        
        .metric-value {
            font-size: 32px;
            color: #2c3e50;
            font-weight: bold;
        }
        
        .metric-description {
            font-size: 12px;
            color: #95a5a6;
            margin-top: 10px;
        }
        
        .figure-section {
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .figure-section h3 {
            color: #34495e;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .comparison-table th {
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        
        .comparison-table td {
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        
        .comparison-table tr:hover {
            background: #f8f9fa;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 30px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            text-align: center;
            font-size: 0.9em;
        }
        
        .info-box {
            background: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
            color: #2980b9;
        }
        
        .warning-box {
            background: #fef5e7;
            border-left: 4px solid #f39c12;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
            color: #d68910;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>M3v2 Firm-Panel Analysis</h1>
            <p>Interactive Dashboard: Consumer Sentiment and Stock Returns</p>
        </div>
        
        <div class="content">
    """
    
    # Add key metrics section
    html_content += create_key_metrics_section()
    
    # Add main findings section
    html_content += """
    <div class="section">
        <h2>Key Findings</h2>
        <div class="info-box">
            <strong>Main Result:</strong> We exploit differences in consumer sentiment sensitivity across firms
            to identify a causal effect on returns using a difference-in-differences framework. Small firms exhibit
            greater sensitivity to lagged Michigan consumer confidence, suggesting differential exposure to
            sentiment-driven demand shocks.
        </div>
        <div class="warning-box">
            <strong>Important Caveat:</strong> Sentiment measures are common across all firms in a given year.
            FE identification comes from differential exposure (small-firm × sentiment interaction), not from raw
            common effects within the two-way FE model.
        </div>
    </div>
    """
    
    # Regression comparison section
    html_table, rsq_fig = create_regression_comparison_table()
    html_content += f"""
    <div class="section">
        <h2>Regression Specifications</h2>
        <div class="figure-section">
            <h3>Model Fit Comparison</h3>
            {rsq_fig.to_html(full_html=False, include_plotlyjs=False)}
        </div>
        <div class="figure-section">
            <h3>Model Specifications Summary</h3>
            {html_table}
        </div>
    </div>
    """

    html_content += create_company_controls_section()
    
    # Coefficient explorer
    coef_fig = create_coefficient_explorer()
    html_content += f"""
    <div class="section">
        <h2>Coefficient Analysis</h2>
        <div class="figure-section">
            <h3>Interactive Coefficient Explorer</h3>
            <p style="color: #7f8c8d; margin-bottom: 15px;">
                Hover over points to see detailed coefficient estimates with confidence intervals. 
                Larger markers indicate more statistically significant effects.
            </p>
            {coef_fig.to_html(full_html=False, include_plotlyjs=False)}
        </div>
    </div>
    """
    
    # Robustness checks
    rob_fig = create_robustness_summary()
    html_content += f"""
    <div class="section">
        <h2>Robustness Checks</h2>
        <div class="figure-section">
            <h3>Sensitivity Analysis</h3>
            <p style="color: #7f8c8d; margin-bottom: 15px;">
                Comparison of baseline coefficients to results under alternative specifications
                (different lags, COVID exclusion, firm-size subsamples, and placebo tests).
            </p>
            {rob_fig.to_html(full_html=False, include_plotlyjs=False)}
        </div>
    </div>
    """
    
    # Diagnostics
    html_content += f"""
    <div class="section">
        <h2>Econometric Diagnostics</h2>
        {create_diagnostic_summary()}
    </div>
    """
    
    # Additional visualizations section
    html_content += """
    <div class="section">
        <h2>Visual Evidence</h2>
        <div class="info-box">
            <strong>Key Visualizations:</strong> Additional figures for DiD event studies, coefficient forests,
            and interaction elasticities are available in the <code>results/figures/</code> folder:
            <ul style="margin-top: 10px;">
                <li><code>m3v2_did_event_study.png</code> - Average returns around GFC and COVID shocks</li>
                <li><code>m3v2_coefficient_comparison.png</code> - Tornado plot of all significant terms</li>
                <li><code>m3v2_model_specifications.png</code> - R-squared comparison and FE indicators</li>
                <li><code>m3v2_interaction_elasticity.png</code> - Sentiment elasticity by firm size</li>
                <li><code>m3v2_group_trends.png</code> - Long-run trends for small vs large firms</li>
                <li><code>m3v2_fe_did_coefficients.png</code> - FE and DiD coefficient estimates with CIs</li>
                <li><code>m3v2_company_regression_dashboard.png</code> - Stepwise company-controls dashboard</li>
            </ul>
        </div>
    </div>
    """
    
    # Data and outputs section
    html_content += """
    <div class="section">
        <h2>Data and Outputs</h2>
        <p style="color: #7f8c8d; margin-bottom: 15px;">
            All analysis files, tables, and figures are available in the <code>results/</code> and <code>data/</code>
            directories of your project workspace:
        </p>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 0.9em; color: #2c3e50;">
            <strong>Tables:</strong> m3v2_ols_full_period_results.csv, m3v2_fe_results.csv, m3v2_did_results.csv, etc.<br>
            <strong>Figures:</strong> m3v2_*.png (11 visualizations)<br>
            <strong>Data:</strong> m3v2_firm_panel.csv (52,337 firm-year observations)<br>
            <strong>Report:</strong> M3v2_interpretation.md (full technical memo)
        </div>
    </div>
    """
    
    # Footer
    html_content += """
        </div>
        
        <div class="footer">
            <p>
                <strong>M3v2 Firm-Panel Analysis Dashboard</strong><br>
                Generated from: panel regression, difference-in-differences estimation, and robustness analysis<br>
                Dataset: US Compustat annual firm data (2005–2021) with Michigan consumer sentiment (2005–2021)<br>
                Sample: 7,295 unique firms, 52,337 firm-year observations
            </p>
        </div>
    </div>
</body>
</html>
    """
    
    return html_content


def main() -> None:
    """Generate the interactive dashboard."""
    results = load_results()
    
    # Create HTML with embedded visualizations
    html_dash = create_html_dashboard(
        results_dict=results,
        figs_dict={}  # Placeholder for additional figures
    )
    
    # Write to file
    DASHBOARD_PATH.write_text(html_dash, encoding="utf-8")
    
    print(f"✓ Interactive dashboard created: {DASHBOARD_PATH}")
    print(f"  Open in a web browser to explore the M3v2 results interactively.")


if __name__ == "__main__":
    main()
