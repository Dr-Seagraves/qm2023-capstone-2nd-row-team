# M3v2 Interpretation: Firm Panel Fixed Effects, DiD, and OLS

## What we estimated
1. **Pooled OLS for the full sample**
   - Outcome: annual firm return proxy from fiscal-year price change and dividends
   - Key regressor: lagged Michigan sentiment
   - Controls: size, leverage, profitability, capex intensity, cash ratio, and R&D intensity
   - Industry controls: 2-digit SIC fixed effects
2. **Pooled OLS for the COVID subsample**
   - Sample: fiscal years 2020 and later
   - Same sentiment and control structure as the full sample
3. **Two-way fixed effects panel model**
   - Outcome: annual firm return proxy
   - Fixed effects: firm FE and year FE
   - Key term: lagged sentiment x small-firm exposure
   - Standard errors: clustered by firm
4. **Difference-in-differences panel model**
   - Treatment proxy: small firms
   - Shock windows: post-GFC and post-COVID
   - Key terms: lagged sentiment x small-firm x post-shock interactions
   - Standard errors: clustered by firm
5. **Company-controls regression ladder**
   - Outcome: annual firm return proxy
   - Sequence: sentiment only, firm size, industry FE, capital structure, sales scale, profitability/liquidity, investment intensity, stock price, and full controls
   - Standard errors: clustered by firm

## Sample sizes
- Full-period OLS observations: **52302**
- COVID-only OLS observations: **3127**
- FE observations: **52302**
- DiD observations: **52302**
- Company-controls ladder observations: **52302**

## Main findings
### 1) Full-period OLS
- Lagged sentiment coefficient: 0.0277
- p-value: 0.4364
- 95% CI: [-0.0421, 0.0976]

### 2) COVID-only OLS
- Lagged sentiment coefficient: 0.0773
- p-value: 0.6576
- 95% CI: [-0.2644, 0.4190]

### 3) Fixed effects panel model
- Lagged sentiment x small-firm exposure: 0.2115**
- p-value: 0.0418
- 95% CI: [0.0078, 0.4152]

### 4) Difference-in-differences panel model
- Lagged sentiment x small-firm x post-GFC: 0.0491
- Lagged sentiment x small-firm x post-COVID: 0.0540

Interpretation in plain language:
- The pooled OLS models estimate the direct association between lagged sentiment and firm returns.
- The FE and DiD models are stricter: year fixed effects absorb the common sentiment level, so the estimable signal is whether small firms are more sensitive to sentiment and whether that sensitivity changes after shocks.
- Positive interaction terms imply small firms load more heavily on sentiment after the relevant shock; negative terms imply the opposite.

## Company-controls ladder
- Baseline lagged sentiment coefficient: 0.025<br>(0.035)
- Full controls lagged sentiment coefficient: 0.004<br>(0.029)
- Full controls R-squared: 0.001
- The stepwise table keeps the same sample and adds size, industry, capital structure, sales scale, profitability, liquidity, investment, and market-valuation controls in a cumulative order.
- This is the cleanest publication table for the company-data story because it shows whether sentiment remains informative after standard corporate controls enter the model.

## Diagnostics
- Breusch-Pagan p-value: **0.8943**
- Maximum VIF: **1.31**
- Residual plots saved for the full-period OLS model.

Interpretation:
- If the Breusch-Pagan p-value is small, heteroskedasticity is present and clustered/robust SEs are the correct response.
- VIFs below conventional danger zones suggest the control set is not dominated by severe multicollinearity.

## Robustness checks
- alternative_lags: baseline=0.0277, check=0.0078, aux=0.0005196542546403013
  - If the sign is stable across lags, the sentiment result is not driven by one arbitrary lag choice.
- exclude_covid_years: baseline=0.0277, check=0.0118, aux=49175.0
  - If the coefficient stays similar when 2020-2021 are removed, the result is not only a pandemic artifact.
- size_subsample_split: baseline=0.0803, check=-0.0501, aux=NA
  - Different coefficients across firm-size subsamples indicate heterogeneity in sentiment sensitivity.
- placebo_pre_period: baseline=0.2115, check=1.7745, aux=0.061726060263125326
  - A weak placebo interaction supports the claim that the crisis DiD is not just capturing generic pre-trends.

## Visual evidence
- `results/figures/m3v2_group_trends.png`: average annual returns for small vs large firms.
- `results/figures/m3v2_did_event_study.png`: event study plots around GFC (2008) and COVID (2020) shocks.
- `results/figures/m3v2_ols_fitted_scatter.png`: actual vs fitted values for the pooled OLS model.
- `results/figures/m3v2_residuals_vs_fitted.png`: residual spread across fitted values.
- `results/figures/m3v2_residuals_qq.png`: Q-Q plot of OLS residuals.
- `results/figures/m3v2_residuals_hist.png`: residual distribution check.
- `results/figures/m3v2_fe_did_coefficients.png`: sentiment and shock interaction coefficients.
- `results/figures/m3v2_coefficient_comparison.png`: tornado plot of coefficients across specifications.
- `results/figures/m3v2_model_specifications.png`: R-squared comparison and FE indicators.
- `results/figures/m3v2_interaction_elasticity.png`: sentiment elasticity by firm size (FE model).
- `results/figures/m3v2_company_regression_dashboard.png`: stepwise company-controls dashboard.

## Practical caveat
- This is a genuine firm-year panel, but the sentiment series is still common to all firms in a given year.
- That means the strict FE identification comes from differential exposure, not from a raw common-sentiment main effect inside the TWFE model.
- The pooled OLS models provide the direct sentiment coefficient; the FE and DiD models provide the panel-based causal-style comparison the rubric asks for.

## Files generated for M3v2
- `data/final/m3v2_firm_panel.csv`
- `results/tables/m3v2_ols_full_period_results.csv`
- `results/tables/m3v2_ols_covid_only_results.csv`
- `results/tables/m3v2_fe_results.csv`
- `results/tables/m3v2_did_results.csv`
- `results/tables/m3v2_bp_test_results.csv`
- `results/tables/m3v2_vif_results.csv`
- `results/tables/m3v2_robustness_checks.csv`
- `results/tables/m3v2_model_comparison_table.csv`
- `results/tables/m3v2_model_comparison_table.md`
- `results/tables/m3v2_company_model_comparison_table.csv`
- `results/tables/m3v2_company_model_comparison_table.md`
- `results/figures/m3v2_group_trends.png`
- `results/figures/m3v2_did_event_study.png`
- `results/figures/m3v2_ols_fitted_scatter.png`
- `results/figures/m3v2_residuals_vs_fitted.png`
- `results/figures/m3v2_residuals_qq.png`
- `results/figures/m3v2_residuals_hist.png`
- `results/figures/m3v2_fe_did_coefficients.png`
- `results/figures/m3v2_coefficient_comparison.png`
- `results/figures/m3v2_model_specifications.png`
- `results/figures/m3v2_interaction_elasticity.png`
- `results/figures/m3v2_company_regression_dashboard.png`