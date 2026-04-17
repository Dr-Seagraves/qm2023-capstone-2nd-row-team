Milestone 3: Econometric Models
QM 2023 Capstone Project
Due: Friday, Week 14 (April 24, 2026) by 11:59 PM Points: 50 (25% of capstone grade) Format: Team
submission via shared GitHub repository (main branch)

Overview
Milestone 3 is the analytical heart of your capstone project. You transition from descriptive EDA (M2) to
causal inference using panel regression techniques. Your goal is to estimate the causal effects of driver
variables (policy shocks, market conditions, economic factors) on your outcome variable.
Real-world context: Decision-makers demand rigorous empirical evidence. A simple correlation ("[outcome]
falls when [driver] rises") is not enough. You must:
Control for confounding variables (fixed effects)
Test assumptions (homoskedasticity, multicollinearity)
Demonstrate robustness (alternative specifications, sensitivity analysis)
Defend your causal identification strategy
Success criterion: Your regression models should be publication-ready and defensible under critical
questioning.

Dataset Adaptation Note
Alternative Dataset Teams: The specifications below use REIT examples, but the methods apply to all
panel/time-series datasets:
Fixed Effects (Model A) → Works for any panel data (Entity × Time structure)
Model B Options → Choose based on your research question:
DiD if you have a policy shock + treatment/control groups
ARIMA if you have a single time series (e.g., aggregate crypto index, national home prices)
ML comparison if you want to test interpretability vs. predictive accuracy
Translation Guidance: See Dataset-Translation-Examples.md for worked examples translating REIT
model specs to Crypto, Housing, and Macro datasets.
Unsure which Model B to choose? If your dataset doesn't have a natural experiment or policy shock,
Option 3 (ML comparison) works for any dataset. It only requires your existing outcome and
predictor variables — no treatment/control groups needed.
Required package: Model A uses linearmodels for PanelOLS. Install it with pip install
linearmodels before starting. If you have trouble installing it, statsmodels OLS with dummy
variables can achieve similar results (ask in office hours).

1 / 11

Learning Objectives
By completing M3, you will:
1. Specify and estimate panel regression models (Fixed Effects, Two-Way FE)
2. Apply causal identification strategies (DiD, time series, or ML comparison)
3. Diagnose assumption violations (heteroskedasticity, multicollinearity, autocorrelation)
4. Implement robustness checks (robust SEs, alternative lags, placebo tests)
5. Interpret coefficients economically (not just statistically)
6. Communicate results through publication-ready regression tables
7. Defend methodological choices with economic reasoning

Deliverables
1. Python Script: capstone_models.py
Requirements:
Runs from top to bottom without errors
Uses relative paths only
Includes clear section headers and comments
Estimates at least two econometric specifications:
Model A: Fixed Effects (REQUIRED)
Model B: One of the following (CHOOSE ONE):
Difference-in-Differences (DiD)
ARIMA time series forecast
Machine Learning comparison (Random Forest vs. OLS)
Outputs publication-ready regression tables (saved to results/tables/) and diagnostic plots (saved to
results/figures/). Use TABLES_DIR and FIGURES_DIR from config_paths.
Structure:

"""
QM 2023 Capstone: Milestone 3 Econometric Models
Team: [Your Team Name]
Members: [List names]
Date: [Submission date]
This script estimates panel regression models to identify causal effects of
[DRIVER VARIABLES] on [OUTCOME VARIABLE]. We estimate Fixed Effects models
and [DiD / ARIMA / ML] as alternative specifications.
"""
# Section 1: Imports and data loading
# from config_paths import FINAL_DATA_DIR, FIGURES_DIR, TABLES_DIR
# Load M1 output: pd.read_csv(FINAL_DATA_DIR / '[dataset]_analysis_panel.csv')
# Section 2: Feature engineering (lags, interactions, dummies)
# Section 3: Model A - Fixed Effects regression
# Section 4: Model B - [DiD / ARIMA / ML comparison]
2 / 11

# Section 5: Diagnostics (heteroskedasticity, VIF, residual plots)
# Section 6: Robustness checks (robust SEs, alternative specs, placebo tests)
# Section 7: Save regression tables and diagnostic plots

2. Required Models
Model A: Fixed Effects Regression (REQUIRED)
Goal: Estimate the within-entity effect of driver variables on outcome while controlling for time-invariant
entity characteristics.
Generic Specification:

[OUTCOME]_it = β₀ + β₁·[DRIVER]_lag_it + β₂·[CONTROL1]_it + β₃·[CONTROL2]_it + α_i
+ δ_t + ε_it
Where:
- [OUTCOME]_it = outcome variable for entity i in time period t
- [DRIVER]_lag_it = key driver variable with optimal lag (from M2 EDA)
- [CONTROL1], [CONTROL2] = control variables
- α_i = Entity fixed effect (controls for time-invariant unobservables)
- δ_t = Time fixed effect (controls for aggregate time shocks)
- ε_it = error term

REIT Example:

ret_it = β₀ + β₁·fedfunds_lag2_it + β₂·MOM_it + β₃·QLTY_it + β₄·SIZE_it + α_i +
δ_t + ε_it
Where:
- ret_it = return for REIT i in month t
- fedfunds_lag2_it = Federal Funds Rate (2-month lag, per M2 EDA)
- MOM, QLTY, SIZE = factor premiums
- α_i = REIT fixed effect
- δ_t = Time fixed effect

Crypto Example:

return_it = β₀ + β₁·reg_severity_lag1_it + β₂·volume_it + β₃·mcap_it + α_i + δ_t +
ε_it
Where:
- return_it = token return for token i in day t
- reg_severity_lag1_it = regulatory sentiment index (1-day lag)
- volume_it = 24-hour trading volume
- mcap_it = market capitalization
3 / 11

Housing Example:

price_growth_it = β₀ + β₁·mortgage_rate_lag3_it + β₂·employment_growth_it +
β₃·inventory_it + α_i + δ_t + ε_it
Where:
- price_growth_it = median home price growth for region i in month t
- mortgage_rate_lag3_it = 30-year mortgage rate (3-month lag)
- employment_growth_it = regional employment growth
- inventory_it = months of housing supply

Implementation:

from linearmodels.panel import PanelOLS
# Set panel structure (use your entity_id and time_var)
data_panel = merged.set_index(['[entity_id]', '[time_var]'])
# Define outcome and predictors
y = data_panel['[outcome]']
X = data_panel[['[driver]_lag[X]', '[control1]', '[control2]', '[control3]']]
# Estimate Fixed Effects model
model_fe = PanelOLS(y, X, entity_effects=True, time_effects=True).fit(
cov_type='clustered', cluster_entity=True
)
print(model_fe.summary)

Expected Output:
Coefficient table with standard errors, t-stats, p-values
R²: within, between, overall
F-statistic for joint significance
Key Question to Answer:
What is the causal effect of a [1 unit / 1% / 1 pp] increase in [DRIVER] on [OUTCOME],
controlling for entity and time fixed effects?

Model B: Choose One of Three Options
Option 1: Difference-in-Differences (DiD)

When to Use: You have a policy shock or event that affects a treatment group but not a control group.
4 / 11

Goal: Estimate the causal effect of the shock on treated entities relative to control entities.
Generic Specification:

[OUTCOME]_it = β₀ + β₁·Treated_i + β₂·Post_t + β₃·(Treated_i × Post_t) + controls
+ ε_it
Where:
- Treated_i = 1 if entity i is in treatment group, 0 otherwise
- Post_t = 1 if time t is after shock, 0 otherwise
- β₃ = DiD estimator (differential effect on treated group post-shock)

REIT Example:

ret_it = β₀ + β₁·Sensitive_i + β₂·Post2022_t + β₃·(Sensitive_i × Post2022_t) +
controls + ε_it
Where:
- Sensitive_i = 1 if REIT i is in rate-sensitive sector (Retail, Office)
- Post2022_t = 1 if month t ≥ January 2022 (start of rate hike cycle)
- β₃ = Differential effect on sensitive sectors post-hike

Crypto Example:

return_it = β₀ + β₁·DeFi_i + β₂·PostCrackdown_t + β₃·(DeFi_i × PostCrackdown_t) +
controls + ε_it
Where:
- DeFi_i = 1 if token i is DeFi protocol, 0 if centralized exchange
- PostCrackdown_t = 1 if day t ≥ SEC enforcement action date

Housing Example:

price_growth_it = β₀ + β₁·Urban_i + β₂·PostHike_t + β₃·(Urban_i × PostHike_t) +
controls + ε_it
Where:
- Urban_i = 1 if region i is urban core, 0 if suburban/rural
- PostHike_t = 1 if month t ≥ start of Fed rate hike cycle

Key Question to Answer:
Did the [policy shock / event] differentially impact [treatment group] compared to [control
group]?
5 / 11

Option 2: ARIMA Time Series Forecast

When to Use: Your dataset is a single time series (no entity dimension) or you want to forecast aggregate
outcomes.
Goal: Forecast [OUTCOME] 6-12 periods ahead using historical patterns.
Generic Specification:

ARIMA(p, d, q) on [OUTCOME] time series
- Use auto_arima to select optimal (p, d, q)
- Test stationarity (ADF test)
- Forecast with 95% confidence bands

Guidance: Aggregate to time series if panel. Use pmdarima.auto_arima for order selection;
statsmodels.tsa.arima.model.ARIMA for fit and forecast(steps=12). Test stationarity (ADF); report
forecast accuracy vs. naive baseline.
Crypto Example: Forecast aggregate crypto market index (Bitcoin dominance-weighted).
Housing Example: Forecast national median home price growth.
Key Question to Answer:
Can historical patterns predict future [OUTCOME]? How accurate is the forecast compared to a
naive "no change" baseline?

Option 3: Machine Learning Comparison (Random Forest vs. OLS)

When to Use: You want to test whether complex nonlinear models improve predictions compared to
interpretable linear regression.
Goal: Compare predictive accuracy of OLS vs. Random Forest; assess interpretability trade-off.
Guidance: Train/test split. Fit OLS (statsmodels) and RandomForestRegressor. Compare R² and RMSE on test
set. Report feature importance; discuss interpretability trade-off.
Key Question to Answer:
Does a more complex model (Random Forest) meaningfully improve predictions compared to
OLS? If so, at what cost to interpretability?

3. Diagnostics (REQUIRED for Model A)
You must run and report the following diagnostic tests:
A. Heteroskedasticity Test
Method: Breusch-Pagan test or visual inspection of residuals
6 / 11

from statsmodels.stats.diagnostic import het_breuschpagan
residuals = model_fe.resids
# For panel models, extract fitted values manually or use OLS as proxy
# Then run het_breuschpagan(residuals, X)

Interpretation: If p < 0.05, heteroskedasticity is present. Solution: Use robust standard errors
(cov_type='clustered').

B. Multicollinearity (VIF)
Method: Variance Inflation Factor for all predictors

from statsmodels.stats.outliers_influence import variance_inflation_factor
vif_data = pd.DataFrame()
vif_data["Variable"] = X.columns
vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in
range(X.shape[1])]
print(vif_data)

Threshold: VIF > 10 indicates problematic multicollinearity. Solution: Drop or combine correlated predictors.

C. Residual Plots
Residuals vs. Fitted: Should show no pattern (random scatter around 0)

from config_paths import FIGURES_DIR
plt.figure(figsize=(10, 6))
plt.scatter(model_fe.fitted_values, model_fe.resids, alpha=0.3)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel('Fitted Values')
plt.ylabel('Residuals')
plt.title('Residuals vs. Fitted Values (Fixed Effects Model)')
plt.savefig(FIGURES_DIR / 'M3_residuals_vs_fitted.png', dpi=300)
plt.show()

Q-Q Plot: Should follow diagonal if residuals are normally distributed

from scipy import stats

7 / 11

stats.probplot(model_fe.resids, dist="norm", plot=plt)
plt.title('Q-Q Plot: Residual Normality Check')
plt.savefig(FIGURES_DIR / 'M3_qq_plot.png', dpi=300)
plt.show()

4. Robustness Checks (REQUIRED)
You must conduct at least 3 of the following robustness checks:
1. Robust Standard Errors
Already implemented with cov_type='clustered'
Compare clustered SEs vs. standard SEs (show both in table)
2. Alternative Lag Structures
Test [DRIVER] at different lags (e.g., lag 1, 2, 3 for monthly data; lag 1, 7, 30 for daily data)
Report how coefficients change across lag specifications
Note: M2 EDA identified optimal lag; verify it's robust
3. Exclude Outlier Periods
Re-estimate model excluding crisis periods (e.g., March-May 2020 for COVID, 2008-2009 for financial
crisis)
Compare coefficients: are results driven by outlier periods?
4. Group Subsamples (If Applicable)
Estimate Model A separately for different groups (e.g., sensitive vs. resilient sectors, large vs. small
entities)
Test if driver effects differ across groups
5. Placebo Test (for DiD only)
Run DiD regression as if policy shock occurred in earlier period (pre-treatment)
Should find no significant effect (β₃ ≈ 0, p > 0.10)

5. Regression Tables (Publication-Ready)
Use stargazer (if available) or custom formatting:
Example Table:

=================================================================
Model 1: FE
Model 2: FE
Model 3: DiD
(Baseline)
(Robust SE)
(Policy Shock)
----------------------------------------------------------------8 / 11

[DRIVER] (lag X)

-0.025***
(0.008)

-0.025**
(0.010)

-0.022**
(0.009)

[CONTROL1]

0.042***
(0.012)

0.042***
(0.013)

0.040***
(0.012)

[CONTROL2]

0.031**
(0.014)

0.031**
(0.015)

0.029**
(0.014)

Treated × Post

—

—

-0.035***
(0.011)

----------------------------------------------------------------Entity FE
Yes
Yes
Yes
Time FE
Yes
Yes
Yes
Clustered SE
No
Yes
Yes
N
5,432
5,432
5,432
R² (within)
0.38
0.38
0.41
----------------------------------------------------------------*** p<0.01, ** p<0.05, * p<0.10

Save to CSV:

from config_paths import TABLES_DIR
results_table.to_csv(TABLES_DIR / 'M3_regression_table.csv')

6. Interpretation Memo: M3_interpretation.md
Required sections:
Model A headline: "[1 unit/pp] increase in [DRIVER] → [magnitude] change in [OUTCOME]" with pvalue. Interpret in economic units.
Economic interpretation: 2-3 causal channels (e.g., leverage, discount rate, demand).
Model B summary: DiD/ARIMA/ML results; key takeaway.
Diagnostics: Heteroskedasticity (Breusch-Pagan), VIF, residual plots—implications and fixes.
Robustness: Clustered SEs, alternative lags, outlier exclusions.
Caveats: Omitted variables, parallel trends (DiD), external validity.
See Dataset-Translation-Examples.md for REIT/Crypto/Housing interpretation examples.

7. AI Audit Appendix: AI_AUDIT_APPENDIX.md
Same requirements as M1 and M2. Document all AI use, with emphasis on:
Econometric specification decisions
Diagnostic test interpretations
Robustness check suggestions
9 / 11

Grading Rubric (50 points)
See rubric.md for detailed breakdown. Summary:
Component

Points

Model Specification

15

Diagnostics &
Robustness

12

Interpretation

18

Presentation

5

Criteria
Both models estimated correctly; appropriate for research question;
economically sensible
All required diagnostics run; robustness checks thoughtful; issues
addressed
Coefficients interpreted in economic terms; magnitude assessed;
caveats discussed
Regression tables publication-ready; code clean; memo professional

Total: 50 points

Common Pitfalls and How to Avoid Them
Pitfall 1: Ignoring Fixed Effects
Problem: Running pooled OLS instead of FE; loses causal identification Solution: Always include
entity_effects=True in PanelOLS

Pitfall 2: Not Using Clustered SEs
Problem: Standard errors assume independence; panel data violates this Solution: Use
cov_type='clustered', cluster_entity=True

Pitfall 3: Misinterpreting Coefficients
Problem: "A 1% increase in [DRIVER] increases [OUTCOME] by -2.5%" Correct: "A 1 [unit/pp/%] increase in
[DRIVER] reduces [OUTCOME] by 2.5 [units/pp/%]" Key: Match units in interpretation to units in data

Pitfall 4: Skipping Diagnostics
Problem: Assumes Gauss-Markov holds; reports potentially invalid SEs Solution: Run heteroskedasticity test,
VIF, residual plots for every model

Pitfall 5: No Economic Interpretation
Problem: Memo just reports "β = -0.025, p < 0.01" with no context Solution: Explain WHY economically
(mechanisms, theory, transmission channels)

Testing Checklist (Run Before Submission)
Script runs from scratch without errors
10 / 11

Both Model A (FE) and Model B (DiD/ARIMA/ML) estimated
All diagnostics run (heteroskedasticity, VIF, residual plots)
At least 3 robustness checks conducted
Regression tables saved to results/tables/ (CSV or text format)
Diagnostic plots saved to results/figures/ (PNG)
M3_interpretation.md complete with economic reasoning
AI_AUDIT_APPENDIX.md submitted
Coefficients make economic sense (signs, magnitudes, units)

Submission Instructions
Shared Team Repository Submission
1. Work in your team's shared private GitHub repository and submit by committing/pushing to main.
2. Add your files:

git add capstone_models.py
git add M3_interpretation.md
git add AI_AUDIT_APPENDIX.md
git add results/tables/M3_*.csv
git add results/figures/M3_*.png
git commit -m "M3: Econometric Models submission"
git push origin main

3. Verify: Check GitHub repo; script/tables/figures should be visible, and your latest commit should be on
main.
Deadline: Friday, Week 14 (Apr 24) by 11:59 PM

Resources and Support
Office Hours
Dr. Seagraves: Monday & Wednesday, 3:00-5:00 PM
Focus for M3: Model specification, diagnostic interpretation, robustness strategies

Example Code
Starter script: starter/capstone_models.py
linearmodels docs: Panel OLS guide

Good luck! Rigorous econometrics separates data science from data description.

Document prepared for QM 2023: Statistics II, Spring 2026, University of Tulsa Contact: Dr. Cayman Seagraves
(cayman-seagraves@utulsa.edu)
11 / 11

