# Time-Series Event Study Summary

## Method

This is a single-series event study on aggregate monthly market returns.
For each shock, expected returns are estimated from a pre-event benchmark model:

- Outcome: `mkt_ret`
- Regressors: lagged Michigan sentiment, lagged AAII bull-bear spread, and lagged Fama-French controls (`smb_l1`, `hml_l1`, `rmw_l1`, `cma_l1`)
- Estimation window: months `-60` through `-13` before the event
- Inference in the benchmark model: HAC/Newey-West standard errors with 3 lags
- Event study outputs: abnormal returns and cumulative abnormal returns in the event window

This is the correct design for this repository because the data are a single aggregate monthly time series, not a multi-entity panel.

## Main Results

### 2008 Financial Crisis
- Window [-0, +0]: CAR = -8.612***, t = -3.940, p = 0.0001
- Window [-1, +1]: CAR = -25.207***, t = -6.658, p = 0.0000
- Window [-3, +3]: CAR = -39.317***, t = -6.798, p = 0.0000
- Window [-6, +6]: CAR = -49.650***, t = -6.300, p = 0.0000
- Window [-12, +12]: CAR = -44.145***, t = -4.039, p = 0.0001

### COVID Shock
- Window [-0, +0]: CAR = -12.259***, t = -3.715, p = 0.0002
- Window [-1, +1]: CAR = 0.724, t = 0.127, p = 0.8991
- Window [-3, +3]: CAR = 4.689, t = 0.537, p = 0.5912
- Window [-6, +6]: CAR = 9.398, t = 0.790, p = 0.4296
- Window [-12, +12]: CAR = 21.629, t = 1.311, p = 0.1899

## Benchmark Model Fit

- COVID Shock: estimation window 2015-03-31 to 2019-02-28, N = 48, R-squared = 0.120, residual SD = 3.300
- 2008 Financial Crisis: estimation window 2004-02-29 to 2007-08-31, N = 43, R-squared = 0.078, residual SD = 2.186

## Files Generated
- Table: `/workspaces/qm2023-capstone-2nd-row-team/results/tables/time_series_event_study_window_results.csv`
- Table: `/workspaces/qm2023-capstone-2nd-row-team/results/tables/time_series_event_study_monthly_path.csv`
- Table: `/workspaces/qm2023-capstone-2nd-row-team/results/tables/time_series_event_study_benchmark_models.csv`
- Figure: `/workspaces/qm2023-capstone-2nd-row-team/results/figures/time_series_event_study_paths.png`
- Figure: `/workspaces/qm2023-capstone-2nd-row-team/results/figures/time_series_event_study_window_bars.png`