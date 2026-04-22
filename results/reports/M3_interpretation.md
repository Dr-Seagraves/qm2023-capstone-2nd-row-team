# M3 Interpretation: Fixed Effects and Difference-in-Differences

## What we estimated
1. **Calendar-month fixed effects model for market returns**
   - Outcome: `mkt_ret`
   - Key predictors: lagged Michigan sentiment and lagged AAII bull-bear spread
   - Controls: `smb`, `hml`, `rmw`, `cma`
   - Fixed effects: month-of-year dummies
2. **Model A: Two-way fixed effects (entity and time) on the long panel**
   - Outcome: standardized `value_z` in long-form panel
   - Fixed effects: variable/entity dummies and date fixed effects
   - Standard errors: clustered by entity (`variable`)
   - Shock indicators: post-2008 and post-COVID
3. **Difference-in-differences model for shocks**
   - Treated group: sentiment series (`sentiment_michigan_ics`, AAII sentiment variables)
   - Control group: market return and factor series
   - Interactions: `treated_sentiment x post_gfc` and `treated_sentiment x post_covid`
   - Date fixed effects included
   - Standard errors: clustered by entity (`variable`)

## Sample sizes
- Market FE observations: **251**
- Panel/DiD observations: **3024**

## Main economic interpretation
### 1) Predictive return model
- `sentiment_michigan_ics_l1`: coef = -0.0067, p = 0.8058, 95% CI [-0.0598, 0.0464]
- `bull_bear_spread_l1`: coef = 0.0001, p = 0.9952, 95% CI [-0.0395, 0.0398]

Interpretation in plain language:
- A positive lagged sentiment coefficient would mean stronger confidence last month is associated with higher return this month.
- A negative lagged bull-bear spread coefficient would support a contrarian story (too much bullishness predicts softer next-month returns).
- Factor coefficients capture whether common risk channels still explain returns after sentiment is added.

### 2) Entity fixed effects shock shifts
- `post_gfc`: coef = -0.5316, p = 0.2243, 95% CI [-1.3891, 0.3258]
- `post_covid`: coef = 0.0151, p = 0.9175, 95% CI [-0.2712, 0.3015]

Interpretation in plain language:
- The entity FE model asks whether the average standardized level of series shifts after each macro shock, after controlling for each variable's own baseline level.

### 3) DiD: differential effect on sentiment vs controls
- `treated_sentiment x post_gfc`: coef = 0.2010, p = 0.5609, 95% CI [-0.4763, 0.8783]
- `treated_sentiment x post_covid`: coef = -0.5286**, p = 0.0448, 95% CI [-1.0449, -0.0123]

Interpretation in plain language:
- Positive DiD interaction: sentiment series rose more (or fell less) than return/factor controls after that shock.
- Negative DiD interaction: sentiment series weakened more than controls after that shock.

## Diagnostics
- Breusch-Pagan p-value: **0.0124**
- Max VIF among predictors: **1.58**
- Residual diagnostics saved as residual-vs-fitted, Q-Q, and histogram plots.

Interpretation:
- A low Breusch-Pagan p-value suggests heteroskedasticity risk; we therefore report robust/clustered SEs.
- VIF values well below 10 reduce concern about severe multicollinearity.

## Robustness checks
- `alternative_lags` (sentiment_coef_lag1_vs_lag2_vs_lag3): baseline=0.0035, check=0.0122, aux=0.01092024870131658
  - Signs/magnitudes across lags indicate whether lag choice is sensitive.
- `exclude_covid_crash_window` (did_post_covid_interaction): baseline=-0.5286, check=-0.5484, aux=NA
  - Close values imply COVID interaction is not driven only by the crash window.
- `placebo_pre_gfc` (treated_sentiment:post_placebo): baseline=0.0000, check=-0.4685, aux=0.17289273102453484
  - Small/insignificant placebo effects support DiD identification assumptions.

## Visual evidence
- `results/figures/m3_treated_vs_control_trends.png`: treated vs control paths with 2008 and 2020 markers.
- `results/figures/m3_did_coefficients.png`: DiD point estimates and confidence intervals.
- `results/figures/m3_market_model_fit.png`: observed vs fitted market returns.
- `results/figures/m3_residuals_vs_fitted.png`: residual spread across fitted values.
- `results/figures/m3_residuals_qq.png`: residual normality diagnostic.
- `results/figures/m3_residuals_hist.png`: residual distribution check.

## Applicability and limitations
- The dataset has one aggregate market return series over time, so classic multi-firm panel FE on returns is not directly available.
- The entity FE and DiD are applied on the stacked long panel where each variable acts as an entity.
- This design is useful for testing shock sensitivity across groups of series, but it should not be interpreted as a firm-level causal panel model.
- Robust (HC1) standard errors are used to reduce heteroskedasticity concerns.

## Files generated for M3
- `results/tables/m3_market_fe_results.csv`
- `results/tables/m3_entity_fe_results.csv`
- `results/tables/m3_did_results.csv`
- `results/tables/m3_bp_test_results.csv`
- `results/tables/m3_vif_results.csv`
- `results/tables/m3_robustness_checks.csv`
- `results/tables/m3_model_comparison_table.csv`
- `results/tables/m3_model_comparison_table_no_time_fe.csv`
- `results/tables/m3_model_comparison_table_no_time_fe.md`
- `results/figures/m3_treated_vs_control_trends.png`
- `results/figures/m3_did_coefficients.png`
- `results/figures/m3_market_model_fit.png`
- `results/figures/m3_residuals_vs_fitted.png`
- `results/figures/m3_residuals_qq.png`
- `results/figures/m3_residuals_hist.png`