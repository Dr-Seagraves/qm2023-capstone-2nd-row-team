# M3 Data Structure Summary

## Short Answer

The dataset is used in two different ways:

- The market-return regressions are **time-series regressions** on one monthly market series with lagged sentiment and factor controls.
- The fixed-effects and difference-in-differences regressions are run on a **stacked long panel** where each variable is treated as an entity observed each month.

This means the project does **not** use a traditional stock-level panel. It starts from one monthly merged dataset and reshapes it into long form for the FE and DiD models.

## Shapes Used in Analysis

- Wide monthly dataset: **252 rows x 13 columns**
- Market regression sample after lags: **251 rows x 19 columns**
- Long stacked panel: **3,024 rows x 3 columns**
- Variables in stacked panel: **12**
- Monthly periods: **252**

## What The Dataset Looks Like

### Wide monthly form used for market regressions

| date | bearish_pct | bull_bear_spread | bullish_pct | cma | hml | mkt_ret | mkt_rf | neutral_pct | rf | rmw | sentiment_michigan_ics | smb |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2004-01-31 | 15.0 | 41.88 | 56.88 | 3.33 | 2.42 | 2.22 | 2.15 | 28.13 | 0.07 | -3.6 | 103.8 | 2.54 |
| 2004-02-29 | 30.53 | 11.049999999999995 | 41.58 | -1.17 | 0.95 | 1.46 | 1.4 | 27.89 | 0.06 | 2.13 | 94.4 | -1.57 |
| 2004-03-31 | 42.59 | -11.11 | 31.480000000000004 | -0.98 | 0.23 | -1.23 | -1.32 | 25.93 | 0.09 | 1.65 | 95.8 | 1.73 |
| 2004-04-30 | 21.21 | 28.79 | 50.0 | -2.83 | -3.23 | -1.73 | -1.81 | 28.79 | 0.08 | 3.46 | 94.2 | -1.73 |
| 2004-05-31 | 40.28 | -4.170000000000002 | 36.11 | 0.01 | -0.18 | 1.24 | 1.18 | 23.61 | 0.06 | -1.17 | 90.2 | -0.23 |

### Long stacked form used for FE and DiD

| date | variable | value |
| --- | --- | --- |
| 2004-01-31 | bearish_pct | 15.0 |
| 2004-01-31 | bull_bear_spread | 41.88 |
| 2004-01-31 | bullish_pct | 56.88 |
| 2004-01-31 | cma | 3.33 |
| 2004-01-31 | hml | 2.42 |
| 2004-01-31 | mkt_ret | 2.22 |
| 2004-01-31 | mkt_rf | 2.15 |
| 2004-01-31 | neutral_pct | 28.13 |

## Interpretation

- If you ask, "Does lagged sentiment predict next month's aggregate market return?", that is a **time-series question**.
- If you ask, "Do sentiment variables behave differently from return and factor variables after major shocks?", that is handled with the **stacked panel FE / DiD setup**.
- Because each row in the long panel is a variable-month rather than a firm-month, this is best described as a **synthetic panel constructed from aggregate time-series data**.

## Output Files

- Figure: `/workspaces/qm2023-capstone-2nd-row-team/results/figures/m3_data_structure_overview.png`
- Report: `/workspaces/qm2023-capstone-2nd-row-team/results/reports/m3_data_structure_summary.md`
