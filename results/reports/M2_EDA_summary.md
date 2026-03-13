# M2 EDA Summary

## Key Findings
- Market returns and Michigan sentiment show a correlation of 0.029. The sign and magnitude suggest sentiment is informative, but not a stand-alone predictor.
- Market returns and AAII bull-bear spread correlate at 0.461, indicating retail positioning may matter for near-term pricing.
- The largest absolute lagged relationship appears at 12 months (correlation -0.087), which supports testing lagged sentiment terms in M3.
- Rolling and subsample analyses show the sentiment-return relationship is time-varying, so constant-coefficient models may be misspecified.
- Factor links remain meaningful; the largest absolute control correlation with returns is 0.999, supporting inclusion of standard factor controls.

## Hypotheses for M3
1. **Sentiment effect hypothesis**: Lagged Michigan sentiment predicts monthly market returns after controlling for Fama-French factors.
    - Baseline model: mkt_ret_t = alpha + beta1 * sentiment_michigan_(t-12) + gamma'X_t + epsilon_t
   - Expected sign: positive if higher confidence supports risk-taking and demand for equities.
2. **Retail positioning hypothesis**: AAII bull-bear spread has incremental explanatory power beyond Michigan sentiment.
   - Model extension: include `bull_bear_spread_t` with sentiment and controls.
   - Expected sign: positive contemporaneous association, with potential reversal at longer horizons.
3. **Regime heterogeneity hypothesis**: The sentiment-return relationship differs across periods (pre-crisis, post-crisis, pandemic).
   - Model extension: interact sentiment with regime dummies or estimate subsample models.
   - Expected sign: coefficient magnitude varies by macro regime, strongest during stress transitions.

## Data Quality Flags and M3 Mitigations
- **Outliers**: Extreme return months detected (2008-10, 2009-02, 2009-04, 2011-10, 2020-03, 2020-04, 2020-11).
  - Mitigation: robust standard errors and sensitivity checks with winsorized returns.
- **Missing values**: Total missing cells in the merged panel = 0.
  - Mitigation: no imputation required for baseline; maintain explicit checks in M3 pipeline.
- **Potential heteroskedasticity**: Volatility clustering appears in crisis periods.
  - Mitigation: use heteroskedasticity-robust (HC) or Newey-West standard errors.
- **Potential multicollinearity**: Controls from factor set can co-move.
  - Mitigation: report VIF diagnostics and avoid redundant controls if VIF is high.
