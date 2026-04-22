[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/gp9US0IQ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=22634759&assignment_repo_type=AssignmentRepo)
# QM 2023 Capstone Project

Semester-long capstone for Statistics II: Data Analytics.

## Project Structure

- **code/** — Python scripts and notebooks. Use `config_paths.py` for paths.
- **data/raw/** — Original data (read-only)
- **data/processed/** — Intermediate cleaning outputs
- **data/final/** — M1 output: analysis-ready panel
- **results/figures/** — Visualizations
- **results/tables/** — Regression tables, summary stats
- **results/reports/** — Milestone memos
- **tests/** — Autograding test suite

Run `python code/config_paths.py` to verify paths.

## Interactive Dashboard v2

The project includes a second interactive dashboard that maps variable codes
to readable names using `data/final/data_dictionary.md`.

### Generate dashboard

```bash
python3 code/create_interactive_dashboard_v2.py
```

### Output file

- `results/reports/M2_interactive_dashboard_v2.html`

### Open in browser (dev container)

```bash
"$BROWSER" "results/reports/M2_interactive_dashboard_v2.html"
```

Team Members : Steffi Brewer, Nicholas Langkamp, Katrina Baiza - Nicholas is project manager, Katrina is data analyst and Steffi is the recorder. (we shared the codespace and work equally) 

Direction of research

Researching Consumer Sentiment and the Stock Market Returns, using data from the University of Michigan's Survey of Consumers, AAII Investor Sentiment Survey, Ken French Factor Library and FRED. Research Question: Does retail investor sentiment predict short-term stock market returns, or does it act as a contrarian indicator? This research will help us to find out if the market predicts how people feel, or vice versa. How does the stock market affect consumer emotions? Our research will help us to find out if they are correlated or do consumer's feelings affect the future stock market.
Key Variables include, excess market returns, consumer and investor sentiment, and control factors like interest rates.

Before analysis, we expect that consumer sentiment will have a marginal impact on market returns, we think that at times in our time period (2004-2024) we will see fluctuations in the correlation. 

## Preliminary Hypotheses

Below is the consolidated set of null hypotheses implied by our research questions and exploratory analysis.

1. **H0-1 (Michigan Sentiment Predictability):** Lagged Michigan consumer sentiment has no predictive effect on monthly market returns after controls (coefficient on lagged Michigan sentiment equals 0).
2. **H0-2 (AAII Incremental Predictability):** AAII bull-bear spread has no incremental explanatory power for monthly market returns once Michigan sentiment and controls are included (coefficient on bull-bear spread equals 0).
3. **H0-3 (Contrarian Channel):** Higher investor bullishness is not associated with lower subsequent returns (no contrarian effect).
4. **H0-4 (Consumer Confidence Channel):** Higher consumer sentiment is not associated with higher subsequent returns (no confidence channel effect).
5. **H0-5 (Sentiment Divergence):** Consumer sentiment and investor sentiment are equally uninformative in divergence periods (no differential predictive content when they disagree).
6. **H0-6 (Factor-Augmented Alpha):** Sentiment variables do not explain return variation beyond Fama-French-style controls (all sentiment terms jointly equal 0 in factor-augmented models).
7. **H0-7 (Early Warning in Crises):** Sentiment variables do not provide early warning information before market downturn episodes.
8. **H0-8 (Contemporaneous Correlation):** The contemporaneous correlation between market returns and sentiment measures is 0.
9. **H0-9 (Lag Structure):** Correlations between returns and lagged sentiment (e.g., 1, 2, 3, 6, 12 months) are jointly 0.
10. **H0-10 (Regime Stability):** The sentiment-return relationship is stable across subsamples/regimes (pre-crisis, post-crisis, pandemic), meaning interaction/subsample differences are 0.
11. **H0-11 (Control-Factor Relevance):** Factor controls (such as SMB and HML) have no linear relationship with market returns in our sample.
12. **H0-12 (Seasonality):** Market returns contain no systematic seasonal component (seasonal term equals 0 in decomposition-based interpretation).

These H0 statements can be directly paired with alternative hypotheses in M3 regression/event-study testing and reported with p-values/confidence intervals.


## M3v2 Firm-Panel Regression Deliverables

The repository also includes a newer M3v2 pipeline built from `data/raw/us-comp.csv` so the analysis runs on a real firm-year panel.

- Fixed-effects panel modeling with firm and year effects
- Difference-in-differences specifications with small-firm exposure and shock interactions
- Pooled OLS for the full period and for the COVID subsample
- Diagnostics, robustness checks, and publication-style comparison tables
- **NEW:** Investor-ready interactive dashboard with coefficient explorer and visual evidence

### Run M3v2 pipeline

```bash
/home/codespace/.python/current/bin/python code/capstone_models.py
```

### Generate interactive dashboard

```bash
/home/codespace/.python/current/bin/python code/create_m3v2_interactive_dashboard.py
```

### M3v2 outputs

- **Interactive Dashboard:** `results/reports/M3v2_interactive_dashboard.html` (open in browser for interactive exploration)
- Report memo (root): `M3v2_interpretation.md`
- Report memo (reports folder): `results/reports/M3v2_interpretation.md`
- Tables:
	- `results/tables/m3v2_ols_full_period_results.csv`
	- `results/tables/m3v2_ols_covid_only_results.csv`
	- `results/tables/m3v2_fe_results.csv`
	- `results/tables/m3v2_did_results.csv`
	- `results/tables/m3v2_bp_test_results.csv`
	- `results/tables/m3v2_vif_results.csv`
	- `results/tables/m3v2_robustness_checks.csv`
	- `results/tables/m3v2_model_comparison_table.csv`
	- `results/tables/m3v2_model_comparison_table.md`
- Figures:
	- `results/figures/m3v2_group_trends.png` — Long-run trends for small vs large firms
	- `results/figures/m3v2_did_event_study.png` — **NEW!** Event study plots around GFC (2008) and COVID (2020) shocks
	- `results/figures/m3v2_ols_fitted_scatter.png` — Actual vs fitted values for OLS model
	- `results/figures/m3v2_residuals_vs_fitted.png` — Residual spread across fitted values
	- `results/figures/m3v2_residuals_qq.png` — Q-Q plot of OLS residuals
	- `results/figures/m3v2_residuals_hist.png` — Residual distribution check
	- `results/figures/m3v2_fe_did_coefficients.png` — FE and DiD coefficient estimates with CIs
	- `results/figures/m3v2_coefficient_comparison.png` — **NEW!** Tornado plot of coefficients across specifications
	- `results/figures/m3v2_model_specifications.png` — **NEW!** R-squared comparison and FE indicators
	- `results/figures/m3v2_interaction_elasticity.png` — **NEW!** Sentiment elasticity by firm size (FE model)
