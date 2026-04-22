# Time-Series Dataset Readiness

## Correct Dataset Choice

The correct dataset for the project's aggregate time-series analysis is:

- `/workspaces/qm2023-capstone-2nd-row-team/data/final/analysis_panel_wide.csv`

Why this is the correct version:

- It has **one row per month**.
- It has **one column per variable**.
- It matches the structure used for market-return regressions where `mkt_ret` is the outcome and sentiment/factor series are regressors.
- It is the wide companion file written by the merge pipeline, while `analysis_panel.csv` is the reshaped long file used for stacked FE/DiD analysis.

## Validation Checks

Status: validated and ready for aggregate time-series analysis.

- No duplicate dates
- No missing months
- No missing values
- Correct monthly coverage from 2004-01 to 2024-12

## Dataset Shapes

- Source wide monthly dataset: **252 rows x 13 columns**
- Time-series-ready dataset: **252 rows x 22 columns**
- Event-study-ready dataset: **252 rows x 32 columns**

## Recommended Use

- Use `/workspaces/qm2023-capstone-2nd-row-team/data/final/analysis_time_series_ready.csv` for ARDL / distributed-lag / predictive time-series regressions.
- Use `/workspaces/qm2023-capstone-2nd-row-team/data/final/analysis_event_study_ready.csv` for event-window summaries and simple event-study style plots around 2008-09 and 2020-03.
- Keep `analysis_panel.csv` for the stacked long FE and DiD specifications.

## Notes

- This project is fundamentally an **aggregate monthly time-series dataset**.
- The panel models are created by reshaping that same monthly dataset into long form, so they are not based on firm-level cross sections.
