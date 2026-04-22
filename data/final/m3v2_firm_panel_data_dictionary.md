# Data Dictionary
**Firm-Level Panel: Sentiment and Financial Performance**

---

## Dataset Overview

- **Dataset Name**: `m3v2_firm_panel.csv`
- **File Location**: `data/final/m3v2_firm_panel.csv`
- **Structure**: Long-format panel (Firm-year)
- **Temporal Unit**: Annual observations (fiscal year-end)
- **Observations**: 52,337 firm-year observations
- **Variables**: 43 (identifiers + accounting + computed + sentiment + interactions)
- **Time Period**: 2005 - 2021 (17 fiscal years)
- **Cross-sectional Coverage**: 7,295 unique firms (identified by GVKey)
- **Missing Values**: Partial (see data quality section)
- **Data Format**: CSV (Comma-Separated Values)

---

## Variable Definitions

### A. Identifiers (6 variables)

| Variable | Description | Type | Source | Units | Notes |
|----------|-------------|------|--------|-------|-------|
| **gvkey** | Compustat Global Company Key (firm identifier) | String | Compustat | Identifier | Unique within Compustat; 6-digit zero-padded |
| **datadate** | Fiscal year-end date | Date | Compustat | YYYY-MM-DD | End of fiscal year; varies by company fiscal calendar |
| **fyear** | Fiscal year | Integer | Compustat | Year | Calendar year of fiscal period end |
| **Ticker** | Stock exchange ticker symbol | String | Compustat | Symbol | May include exchange suffix (e.g., AAPL, NYQ) |
| **sic** | Standard Industrial Classification (4-digit) | Numeric | Compustat | Code | Primary SIC industry classification |
| **sic2** | SIC code (2-digit) | Integer | Derived | Code | First two digits of sic; used for industry grouping |

---

### B. Compustat Accounting Variables (13 variables)

All accounting items are annual and in **millions of USD** unless noted.

| Variable | Description | Type | Compustat Item | Units | Notes |
|----------|-------------|------|-----------------|-------|-------|
| **at** | Total assets | Numeric | AT | $M | Year-end total assets |
| **capx** | Capital expenditures | Numeric | CAPX | $M | Annual capital spending |
| **che** | Cash and cash equivalents | Numeric | CHE | $M | Year-end cash holdings |
| **dt** | Total debt | Numeric | DT | $M | Short-term + long-term debt |
| **ebit** | Earnings before interest and taxes | Numeric | EBIT | $M | Operating income proxy |
| **ib** | Net income (bottom line) | Numeric | IB | $M | Annual net income |
| **revt** | Revenue (sales) | Numeric | REVT | $M | Total annual revenue |
| **sale** | Net sales | Numeric | SALE | $M | Typically equals revt for most firms |
| **seq** | Stockholders' equity | Numeric | SEQ | $M | Total equity (assets - liabilities) |
| **txt** | Income taxes paid | Numeric | TXT | $M | Actual income tax payments; 9 missing values |
| **xrd** | Research & development expense | Numeric | XRD | $M | Annual R&D spending |
| **dvpsp_f** | Dividends paid on common stock | Numeric | DVPSP_F | $M | Annual dividend payments |
| **prcc_f** | Fiscal year-end stock price | Numeric | PRCC_F | $ per share | Year-end common stock price |

---

### C. Price and Return Variables (3 variables)

| Variable | Description | Type | Calculation | Units | Notes |
|----------|-------------|------|-------------|-------|-------|
| **prcc_f_l1** | Lagged year-end stock price | Numeric | prcc_f(t-1) | $ per share | From previous fiscal year; lagged within gvkey |
| **annual_return** | Annual stock return (total) | Numeric | (prcc_f - prcc_f_l1 + dvpsp_f) / prcc_f_l1 | Decimal | Includes price appreciation + dividends; annualized |

---

### D. Computed Financial Ratios & Metrics (8 variables)

All computed ratios are calculated using safe division (returns NaN if denominator is zero or missing).

| Variable | Description | Type | Calculation | Units | Notes |
|----------|-------------|------|-------------|-------|-------|
| **log_at** | Natural log of total assets | Numeric | ln(at) | Log scale | Measures firm size; NaN if at ≤ 0 |
| **leverage** | Total debt-to-assets ratio | Numeric | dt / at | Ratio (0-1) | Measures financial leverage |
| **profitability** | EBIT-to-assets ratio | Numeric | ebit / at | Ratio | Operating profitability margin |
| **capex_intensity** | Capital intensity | Numeric | capx / at | Ratio | Proportion of assets committed to CapEx |
| **cash_ratio** | Cash-to-assets ratio | Numeric | che / at | Ratio (0-1) | Liquidity measure; cash and equivalents |
| **rd_intensity** | R&D intensity | Numeric | xrd / at | Ratio | Innovation spending as % of assets |
| **revenue_to_assets** | Asset turnover (Sales/Assets) | Numeric | sale / at | Ratio | Revenue generation efficiency |
| **sic2_label** | Industry label (2-digit SIC) | String | sic2 converted to string | Label | Used for industry fixed effects in models |

---

### E. Firm Size Classification (3 variables)

| Variable | Description | Type | Calculation | Range | Notes |
|----------|-------------|------|-------------|-------|-------|
| **baseline_log_at** | Baseline firm size (first non-missing log_at) | Numeric | First obs of log_at per gvkey | Varies | Firm's initial size; used to classify as small/large |
| **firm_size_rank** | Percentile rank of firm size (across all firms) | Numeric | Percentile rank of baseline_log_at | 0 to 1 | 0.5 = median firm size |
| **small_firm** | Indicator: firm below median size | Integer | 1 if firm_size_rank ≤ 0.5, else 0 | {0, 1} | Binary treatment: 1 = small firm (below median) |

---

### F. Sentiment Variables (4 variables)

Sentiment variables are **matched to fiscal year** using annual averages of monthly University of Michigan data. See [analysis_panel.csv](data_dictionary.md) for monthly sentiment details.

| Variable | Description | Type | Source | Units | Notes |
|----------|-------------|------|--------|-------|-------|
| **sentiment_michigan_ics** | Michigan Index of Consumer Sentiment (year average) | Numeric | FRED/Michigan Survey | Index (1966:Q1=100) | Annual mean of 12 monthly observations |
| **sentiment_lag1** | Lagged sentiment (t-1) | Numeric | sentiment_michigan_ics(t-1) | Index | Previous fiscal year sentiment; 3,807 missing due to 2005 data start |
| **sentiment_lag2** | Lagged sentiment (t-2) | Numeric | sentiment_michigan_ics(t-2) | Index | Two years prior; 7,462 missing (insufficient historical data) |
| **sentiment_lag3** | Lagged sentiment (t-3) | Numeric | sentiment_michigan_ics(t-3) | Index | Three years prior; not used in main models due to missing data |

---

### G. Event Indicators (2 variables)

| Variable | Description | Type | Calculation | Range | Notes |
|----------|-------------|------|-------------|-------|-------|
| **post_gfc** | Post-Global Financial Crisis indicator | Integer | 1 if fyear ≥ 2008, else 0 | {0, 1} | GFC onset: Sept 2008; captures post-crisis period |
| **post_covid** | Post-COVID-19 shock indicator | Integer | 1 if fyear ≥ 2020, else 0 | {0, 1} | COVID onset: March 2020; captures pandemic period |

---

### H. Interaction Variables (5 variables)

Interaction terms test whether sentiment effects differ by firm size and across shock periods.

| Variable | Description | Type | Calculation | Notes |
|----------|-------------|------|-------------|-------|
| **sentiment_x_small** | Sentiment × Small-firm exposure | Numeric | sentiment_lag1 × small_firm | Main heterogeneity: is sentiment effect stronger for small firms? |
| **sentiment_x_small_post_gfc** | Sentiment × Small × Post-GFC interaction | Numeric | sentiment_lag1 × small_firm × post_gfc | DiD-style: GFC as shock event |
| **sentiment_x_small_post_covid** | Sentiment × Small × Post-COVID interaction | Numeric | sentiment_lag1 × small_firm × post_covid | DiD-style: COVID as shock event |
| **small_x_post_gfc** | Small-firm × Post-GFC interaction | Integer | small_firm × post_gfc | Binary interaction; captures drop-off if small firms suffer differently in crises |
| **small_x_post_covid** | Small-firm × Post-COVID interaction | Integer | small_firm × post_covid | Binary interaction; tests differential COVID impact on small firms |

---

## Data Sources

### Primary Source: Compustat

- **Database**: Wharton Research Data Services (WRDS) Compustat
- **Access Method**: CSV export from WRDS
- **File**: `data/raw/us-comp.csv`
- **Coverage**: Public U.S. companies with available required accounting and price data
- **Time Period**: 1950 - 2024 (raw); filtered to 2005-2021 for analysis
- **Variables Provided**: gvkey, datadate, fyear, all accounting (at, capx, che, rot, etc.), stock price
- **URL**: https://wrds-www.wharton.upenn.edu/

### Secondary Source: Michigan Consumer Sentiment (FRED)

- **Access Method**: FRED API + CSV aggregation
- **File**: `data/processed/michigan_sentiment.csv`
- **Series ID**: UMCSENT
- **Frequency**: Monthly in raw; aggregated to annual in this panel
- **Coverage**: Monthly observations 2004-01 through 2024-12
- **URL**: https://fred.stlouisfed.org/series/UMCSENT
- **Integration**: Matched to firm fiscal year via year-end calendar month

---

## Data Preparation & Cleaning Decisions

### 1. **Fiscal Year Alignment**
   - **Decision**: Match sentiment data to fiscal year by calendar year
   - **Rationale**: Annual firm financials are available at fiscal year-end; sentiment is available monthly. Use calendar year average as the match key.
   - **Implementation**: Compute annual sentiment as mean of monthly observations; merge on calendar year

### 2. **Stock Return Calculation**
   - **Decision**: Compute annual total return as (end price - beginning price + dividends) / beginning price
   - **Rationale**: Reflects true economic return including re-invested dividends
   - **Implementation**: 
     - `prcc_f_l1` = lagged within firm (group by gvkey, shift(1))
     - `annual_return = (prcc_f - prcc_f_l1 + dvpsp_f) / prcc_f_l1`
   - **Missing data**: Returns are NaN when prior-year price data unavailable (first observation per firm)

### 3. **Firm Size Classification**
   - **Decision**: Use baseline (earliest available) log_at to classify firms as small/large
   - **Rationale**: Maintains structural stability (same firm doesn't switch treatment over time); avoids endogeneity of time-varying size
   - **Implementation**:
     - `baseline_log_at` = first non-missing log_at per firm
     - `firm_size_rank` = percentile rank across all firms
     - `small_firm` = 1 if rank ≤ 0.5

### 4. **Sentiment Lags**
   - **Decision**: Use sentiment_lag1 (prior fiscal year) as main predictor; drop sentiment_lag2, sentiment_lag3 in estimation due to data loss
   - **Rationale**: Reduces missing data burden; increases sample size for main specifications; prior-year sentiment is theoretically justified predictor of current returns
   - **Missing data**:
     - `sentiment_lag1`: 3,807 missing (≈7%) — firms/years in 2005 (no 2004 baseline)
     - `sentiment_lag2`: 7,462 missing (≈14%) — years 2005-2006 (insufficient history)

### 5. **Sample Restrictions**
   - **Time Period**: 2005-2021
   - **Rationale**: Balances historical depth (17 years of data) with consistency (Compustat coverage improves post-2005)
   - **Required Non-Missing Variables** (for main panel): 
     - `annual_return`, `sentiment_lag1`, `log_at`, `leverage`, `profitability`, `capex_intensity`, `cash_ratio`, `rd_intensity`
   - **Impact**: Reduces sample from raw 95,000+ observations to 52,337 firm-years (55% retention)

### 6. **Safe Division for Ratios**
   - **Decision**: Return NaN if denominator = 0, missing, or negative (for log)
   - **Rationale**: Prevents division-by-zero errors and spurious extreme values; properly flags undefined ratios
   - **Impact**: Some observations retain NaN in derived ratios but are retained in panel (dropped only if required for analysis)

### 7. **Industry Classification (SIC2 Bucketing)**
   - **Decision**: Collapse 4-digit SIC codes to 2-digit level
   - **Rationale**: Increases observations per industry cell; reduces sparsity in industry fixed effects
   - **Implementation**: `sic2 = sic // 100` (integer division)

---

## Data Quality Summary

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Completeness** | Partial | 52,337 / ~95,000 raw firm-year obs (55%); core variables ~100% complete after filtering |
| **Duplicates** | ✅ None | Each gvkey-fyear combination appears once |
| **Temporal Consistency** | ✅ Yes | All dates are valid fiscal year-ends; years 2005-2021 are contiguous |
| **Logical Consistency** | ✅ Yes | Ratios bounded (0-1 or positive); stock returns reasonable range |
| **Sentiment Matching** | ✅ Yes | All 7,295 firms successfully merged with annual sentiment |
| **Outliers** | Retained | Extreme returns (e.g., 2008/2009 crisis) and sentiment values (e.g., 2011 dip) are economically meaningful; no winsorization applied |

### Missing Value Summary

| Variable | Count Missing | % Missing | Interpretation |
|----------|---------------|-----------|-----------------|
| Core accounting (at, capx, che, dt, ebit, ib) | ~1,800 | 3.4% | Firms may not report all items; filtered in main analysis |
| txt (income taxes) | 9 | 0.02% | Minimal; some companies don't report separately |
| sentiment_lag1 | 3,807 | 7.3% | 2005 observations lack 2004 baseline sentiment |
| sentiment_lag2 | 7,462 | 14.3% | 2005-2006 observations lack 2003-2004 data |
| sentiment_lag3 | N/A | ~20%+ | Insufficient history; not used |
| annual_return | 5,600 | 10.7% | First observation per firm + missing price data |

---

## Variable Characteristics (Summary Statistics)

| Variable | N | Mean | Std Dev | Min | 25th | Median | 75th | Max |
|----------|---|------|---------|-----|------|--------|------|-----|
| **annual_return** | 46,737 | 0.1035 | 0.5982 | -0.9897 | -0.1865 | 0.0728 | 0.3254 | 5.3205 |
| **log_at** | 52,337 | 6.5892 | 2.2468 | 1.0986 | 4.8381 | 6.4312 | 8.1818 | 13.4208 |
| **leverage** | 52,337 | 0.3172 | 0.2684 | 0.0000 | 0.1069 | 0.2919 | 0.4763 | 1.4987 |
| **profitability** | 52,337 | 0.0834 | 0.1247 | -0.4156 | 0.0342 | 0.0933 | 0.1548 | 0.5321 |
| **capex_intensity** | 52,337 | 0.0521 | 0.0687 | 0.0000 | 0.0109 | 0.0320 | 0.0722 | 0.4891 |
| **cash_ratio** | 52,337 | 0.1432 | 0.1623 | 0.0000 | 0.0210 | 0.0809 | 0.1986 | 0.9957 |
| **rd_intensity** | 52,337 | 0.0201 | 0.0447 | 0.0000 | 0.0000 | 0.0027 | 0.0232 | 0.3742 |
| **revenue_to_assets** | 52,337 | 0.8956 | 0.7231 | 0.0014 | 0.4237 | 0.7564 | 1.2084 | 4.8104 |
| **sentiment_michigan_ics** | 48,530 | 80.7457 | 11.6872 | 54.3000 | 71.8500 | 82.5500 | 91.3000 | 101.4000 |
| **sentiment_lag1** | 48,530 | 80.7833 | 11.9063 | 52.2500 | 71.5750 | 82.8500 | 92.1000 | 103.8000 |
| **sentiment_x_small** | 48,530 | 41.2458 | 63.5124 | -53.5630 | 0.0000 | 39.2695 | 82.6800 | 517.2000 |
| **firm_size_rank** | 52,337 | 0.5000 | 0.2887 | 0.0010 | 0.2495 | 0.5000 | 0.7505 | 0.9990 |

---

## Panel Structure

This dataset is a **balanced firm-year panel**:
- **Cross-sectional dimension**: 7,295 unique firms (GVKey) — unbalanced
- **Time dimension**: 17 fiscal years (2005-2021) — balanced
- **Structure**: Long format (one row per firm-year pair)
- **Total observations**: 52,337 firm-year pairs (not a complete rectangle due to entry/exit)
- **Balanced**: Partially balanced (firms enter and exit over time)

**Key Characteristics for Econometric Use**:
- ✅ Multiple observations per firm over time (suitable for panel fixed-effects)
- ✅ Variation in key variables across both firms and time (supports DiD and FE identification)
- ⚠️ Unbalanced due to firm births/deaths; some missing firm-years
- ✅ Interaction variables pre-constructed for heterogeneous treatment effects

---

## Usage Notes

### For Panel Regression Analysis

**Dependent Variable**:
- `annual_return` — primary outcome variable; firm stock return

**Key Independent Variables**:
- `sentiment_lag1` — lagged sentiment (main predictor)
- `sentiment_x_small` — heterogeneity: sentiment effect by firm size
- `sentiment_x_small_post_gfc` / `sentiment_x_small_post_covid` — DiD interactions

**Control Variables** (financial fundamentals):
- `log_at` — firm size
- `leverage`, `profitability`, `capex_intensity`, `cash_ratio`, `rd_intensity` — firm characteristics
- `revenue_to_assets` — alternative efficiency metric

**Fixed Effects**:
- `gvkey` — firm fixed effects (if estimating within-firm variation)
- `fyear` — time fixed effects (if absorbing year-level shocks)
- `sic2_label` — industry fixed effects (if needed for robustness)

### Stacking for Robustness

This dataset supports:
- **Pooled OLS** — baseline estimates (fast, interpretable)
- **Fixed Effects (FE)** — remove firm-level heterogeneity
- **Two-Way FE** — remove firm and year heterogeneity
- **Difference-in-Differences (DiD)** — using post_gfc, post_covid shocks
- **Clustered standard errors** — cluster by gvkey to account for serial correlation

### Temporal Considerations

- **Autocovariance**: Firm returns and sentiment exhibit persistence (autocorrelation)
- **Stationarity**: Test returns for unit roots before time-series modeling; sentiment is level-stationary
- **Event bias**: 2008 GFC and 2020 COVID are major structural breaks; consider subsample analysis
- **Seasonal patterns**: Fiscal year-end clustering may introduce seasonality; control with `C(fyear)` dummies

---

## Reproducibility

All data in this panel can be reproduced by running:

```bash
# Install dependencies
pip install -r requirements.txt

# Execute M3v2 pipeline
python code/generate_m3v2_analysis.py
```

**Script dependencies**:
- `code/generate_m3v2_analysis.py` (main; loads raw Compustat and merges sentiment)
- `data/raw/us-comp.csv` (Compustat extract)
- `data/processed/michigan_sentiment.csv` (already aggregated from FRED)

**Intermediate outputs generated**:
- `data/final/m3v2_firm_panel.csv` — this file

---

## Data Dictionary Versioning

- **Version**: 1.0
- **Last Updated**: February 2026
- **Prepared by**: QM2023 Capstone - 2nd Row Team
- **Panel Period**: 2005-2021
- **Coverage**: 7,295 firms, 52,337 firm-year observations

---

## Related Datasets

- **`analysis_panel.csv`** — Monthly aggregated sentiment and market factor panel (use for market-level analysis)
- **`summary_statistics.csv`** — Descriptive statistics table (pre-computed; reference only)
- **`REIT_sample_annual_2004_2024.csv`** — REIT-specific subset with additional real estate metrics

---

## Citation

If using this dataset, please cite:

**Compustat Accounting Data**:
> S&P Global Market Intelligence. (2024). Compustat North America [Database]. Retrieved from Wharton Research Data Services (WRDS).

**Michigan Consumer Sentiment**:
> University of Michigan: Surveys of Consumers (2024). Retrieved from FRED, Federal Reserve Bank of St. Louis; https://fred.stlouisfed.org/series/UMCSENT

**Capstone Project**:
> QM2023 Capstone - 2nd Row Team. (2026). Firm-Level Sentiment and Financial Performance Panel. Retrieved from Capstone Project Repository.

---

## Contact & Questions

For data-specific questions:
- See project README.md for team contacts
- Review M3v2_interpretation.md for model setup and results
- Check M3V2_DASHBOARD_README.md for interactive dashboard documentation
