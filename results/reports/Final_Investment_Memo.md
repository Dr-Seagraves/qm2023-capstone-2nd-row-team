# MEMORANDUM

**TO:** Investment Committee

**FROM:** 2nd Row Team - Steffi Brewer, Nicholas Langkamp, Katrina Baiza

**DATE:** 1 May 2026

**RE:** Consumer and Investor Sentiment as a Timing Signal for U.S. Equity Returns

## Executive Summary

We analyzed 252 monthly observations from January 2004 through December 2024 to test whether consumer and investor sentiment help explain U.S. equity market performance. Our panel combines the University of Michigan Consumer Sentiment Index, the AAII bull-bear spread, and Fama-French factor data. The clearest takeaway is that sentiment is not a strong stand-alone market-timing rule, but it becomes more informative when we focus on periods of stress and on firms with greater exposure to small-cap risk.

In the aggregate monthly market data, Michigan sentiment has only a weak relationship with returns, while AAII positioning is more closely aligned with near-term market moves. In our M3 time-series specifications, the direct sentiment coefficients were small and statistically weak, which means the data do not support a simple claim that sentiment alone predicts broad market returns. However, the relationship is not meaningless: the effect is economically more relevant when markets are changing regime, which is exactly when investors care most about risk exposure and liquidity.

Our recommendation is to treat sentiment as a regime indicator, not as a standalone trading signal. For a portfolio committee, that means using sentiment to tilt exposure toward more sentiment-sensitive small firms only when sentiment is improving after a shock, and to avoid relying on sentiment alone for broad market timing. The right action is not to buy or sell the entire market on sentiment; it is to use sentiment as one input into sector, size, and risk-budget decisions.

## Methodology

### Data Sources

**Primary sentiment and market data**

- University of Michigan Consumer Sentiment Index from FRED, series `UMCSENT`, monthly coverage filtered to 2004-2024.
- AAII Investor Sentiment Survey, manually collected from the AAII member file and aggregated from weekly observations to month-end.
- Kenneth R. French Data Library factor series, including the market excess return and standard Fama-French controls.

**Firm-level extension for M3v2**

- Repository-provided firm-year panel built from `data/raw/us-comp.csv`, combined with lagged sentiment and firm controls.

### Sample Construction

The final monthly analysis sample is a balanced panel with 252 months and 13 variables, yielding 3,276 complete observations and zero missing values after harmonization. AAII weekly sentiment was collapsed to month-end by keeping the last observation in each month so that all series use the same time unit. The M3v2 firm panel expands the analysis to 52,302 firm-year observations, which allows us to test whether sentiment matters more for smaller firms than for the market as a whole.

The sample covers major macro regimes that matter economically: the 2008 financial crisis, the long post-crisis expansion, the COVID shock and recovery, and the 2022 inflation and tightening cycle. That time span is important because sentiment effects are unlikely to be constant across calm and crisis periods.

### M1 Data Quality and Merge Decisions

The M1 work matters because the final memo depends on the credibility of the merged dataset. We verified that all three sources could be aligned to the same month-end timeline and that the final panel had no missing cells. That result is economically important because it means the later regressions are not being driven by ad hoc imputation or by a short sample created by incomplete matching.

We also preserved the full crisis sample rather than trimming extreme values. That decision is defensible because shocks such as the 2008 collapse and the 2020 pandemic are exactly the kinds of episodes an investor would want a sentiment model to recognize. In other words, the outliers are not noise to be removed; they are the market states most relevant to the investment decision.

The AAII series required a frequency conversion from weekly to monthly. We used the last observation in each month instead of a monthly average because month-end positioning is the quantity most directly linked to next-month pricing pressure. Averaging would smooth away the very variation that could matter for short-run returns, so the month-end rule is the cleaner economic choice.

### Model Specifications

We used three complementary designs.

1. **Aggregate monthly return model:**

   $$
   mkt\_ret_t = \alpha + \beta_1\,sentiment\_michigan_{t-1} + \beta_2\,bull\_bear\_spread_{t-1} + \gamma'X_{t-1} + \varepsilon_t
   $$

   where $X$ includes the Fama-French factor controls. This specification asks whether sentiment contains useful short-run information for the broad market.

2. **Event-study design:**

   We estimated abnormal returns around the 2008 crisis and the COVID shock using a pre-event benchmark model. This design helps separate routine monthly variation from economically meaningful market breaks.

3. **M3v2 firm-panel models:**

   $$
   return_{it} = \alpha_i + \delta_t + \beta\,(sentiment_{t-1} \times small\_firm_i) + \theta'Z_{it} + \varepsilon_{it}
   $$

   and a DiD version that interacts sentiment exposure with post-shock indicators. Here, $\alpha_i$ captures time-invariant firm traits and $\delta_t$ captures common year shocks.

Standard errors are robust or clustered at the firm level, depending on the specification. The key variable definitions are straightforward: Michigan sentiment measures consumer confidence, AAII bull-bear spread measures retail investor positioning, and the Fama-French factors capture common market risk premia that would otherwise confound the sentiment effect.

## Results

### Table 1. Main Findings Across the Project

| Analysis | Key result | Economic interpretation |
| --- | --- | --- |
| M2 aggregate correlations | Market returns correlate weakly with Michigan sentiment (0.029) and more strongly with AAII bull-bear spread (0.461) | Retail positioning tracks market moves more closely than broad consumer confidence |
| M3 aggregate time-series models | Direct sentiment coefficients are near zero and statistically weak | Sentiment alone is not a reliable market-timing rule |
| M3 event study | 2008 and COVID both produce large negative cumulative abnormal returns around the shock window | Sentiment matters most when markets reprice risk abruptly |
| M3v2 firm-panel FE model | Sentiment x small-firm exposure is positive and statistically significant (about 0.21, p < 0.05) | Small firms are more sentiment-sensitive than large firms |
| M3v2 DiD model | Post-shock sentiment interactions remain positive but smaller | The effect is concentrated in stress transitions rather than steady-state periods |

### Table 2. Why M3 Did Not Deliver a Clean Broad-Market Alpha Signal

| Diagnostic | What we saw | Why it matters |
| --- | --- | --- |
| Pooled OLS | Sentiment coefficients were small and insignificant | No evidence of a stable direct market-timing effect |
| Alternative lags | Coefficients changed materially with lag choice | The signal is fragile, not a robust trading rule |
| Placebo and exclusion checks | Placebo effects were small and the COVID exclusion check was similar | Some identifying assumptions are acceptable, but the economic signal is still weak |
| Low explanatory power | R-squared remained very low in the aggregate models | Sentiment is only one small component of return variation |

### Economic Interpretation

The M2 EDA told us that sentiment is informative, but not uniformly so. The AAII spread matters more than Michigan sentiment in the short run, which is consistent with the idea that active investors move prices faster than households do. That is an economically intuitive result: retail positioning can influence marginal demand for equities even if the broader public mood is slower to adjust.

The M3 failure is also informative. When we tried to force the aggregate sentiment relationship into a direct predictive model, the coefficients largely disappeared. That is not a technical nuisance; it is an economic result. It suggests that broad equity prices already incorporate much of the sentiment information, or that sentiment only matters when it shifts exposure, leverage, or funding conditions rather than when it moves in isolation.

The M3v2 firm-panel results sharpen the story. The positive sentiment-by-small-firm interaction means the same change in sentiment has a larger effect on firms that are more exposed to financing frictions, lower visibility, and tighter liquidity. Economically, that fits the idea that smaller firms are more sensitive to discount-rate changes and to changes in investor willingness to hold risk. In plain language, sentiment does not move all firms equally; it matters more when capital is scarce and investors are nervous.

The event-study results reinforce that interpretation. During the 2008 crisis, the cumulative abnormal return was sharply negative across every window we checked, with the most severe damage concentrated around the event month itself and the surrounding quarter. That is consistent with a market that is repricing default risk, funding stress, and recession probability all at once. COVID shows the same mechanism in faster motion: the immediate shock was severe, but the surrounding window recovered more quickly than 2008, which suggests the market interpreted the pandemic as a temporary collapse in activity followed by policy support and normalization. Those are not just statistical patterns; they are a map of how investors process new information.

### Figures to Include

- [Figure 1: M2 rolling correlation and lag structure](../figures/M2_05_rolling_correlation.png)
- [Figure 2: M3v2 small vs large firm trends](../figures/m3v2_group_trends.png)
- [Figure 3: M3v2 event study around the GFC and COVID shocks](../figures/m3v2_did_event_study.png)
- [Figure 4: M3v2 residual diagnostics](../figures/m3v2_residuals_vs_fitted.png)

## Conclusions & Recommendations

The main investment conclusion is simple: sentiment is useful as a context variable, but it is too noisy to drive a broad market allocation on its own. The strongest practical use case is to adjust risk exposure when the market is moving from crisis to recovery or when small-cap firms are especially exposed to changing investor mood. That means sentiment should be used as a second-stage filter, not as a single-signal trading system.

For a portfolio committee, the most defensible action is to keep core market exposure diversified while using sentiment to tilt within the equity book. When sentiment improves after a shock, the committee can justify a modest overweight to smaller, more sentiment-sensitive firms. When sentiment deteriorates, the committee should do the opposite and reduce exposure to the most financing-sensitive names. This is more economically sound than trying to predict the exact next-month market return.

Scenario-wise, the memo supports a simple rule set. In a recovery phase after a market break, rising AAII sentiment and improving Michigan sentiment can justify a small-cap risk tilt because that is where the sensitivity is strongest. In a tightening or stress phase, the same signals argue for reducing exposure to the most rate- and liquidity-sensitive names, especially firms that rely heavily on outside financing. If the committee wants a broad-market hedge, the safer response is to lean on factor tilts such as quality or lower leverage rather than trying to make sentiment itself do all the forecasting work.

The main caveat is that our broad-market M3 models did not produce strong standalone predictive power. That weakness is not a failure of the project; it is an honest result that helps define the boundaries of the signal. The analysis is also limited to U.S. data from 2004-2024, so the findings may not generalize to other countries, longer samples, or regimes with structurally different monetary policy. Finally, sentiment itself can be endogenous to market moves, so the cleanest interpretation is as a regime and exposure measure rather than a literal causal shock.

That caveat also affects how the final recommendation should be phrased. We should not promise alpha from sentiment alone. Instead, we should present sentiment as a useful risk-management overlay that helps decide when the committee should take more or less equity risk, and which part of the equity market is most likely to benefit from that risk budget.

## References

- Federal Reserve Economic Data. University of Michigan Consumer Sentiment Index, UMCSENT. https://fred.stlouisfed.org/series/UMCSENT
- American Association of Individual Investors. Sentiment Survey. https://www.aaii.com/sentimentsurvey
- Kenneth R. French Data Library. https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- Repository data file: `data/raw/us-comp.csv`
- [Optional] Add any course-approved academic citations your team wants to reference in the final PDF.

## Appendix: AI Audit

AI was used to help draft the memo structure, translate regression outputs into plain business language, and tighten the wording of the recommendations. The final content was checked against the M1 data-quality summary, the M2 EDA summary, the M3 regression tables, and the M3v2 interpretation notes.

One important correction was to emphasize that the original M3 broad-market sentiment models did not generate a stable direct alpha signal. The AI draft initially leaned too hard toward a positive-sounding conclusion, so we revised the memo to make the failure explicit and economically meaningful. The memo also preserves editable placeholders so the team can insert final names, dates, and any judgment calls that are specific to the submission version.