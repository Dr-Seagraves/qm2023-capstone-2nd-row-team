# Data Dictionary
**Sentiment and Financial Market Factors Analysis Panel**

---

## Dataset Overview

- **Dataset Name**: `sentiment_analysis_panel.csv`
- **File Location**: `data/final/analysis_panel.csv`
- **Structure**: Long-format panel (Time series)
- **Temporal Unit**: Monthly observations (end-of-month)
- **Observations**: 252 months
- **Variables**: 13 (1 date + 12 data variables)
- **Time Period**: January 2004 - December 2024 (21 years)
- **Missing Values**: 0 (complete panel)
- **Data Format**: CSV (Comma-Separated Values)

---

## Variable Definitions

| Variable Name | Description | Type | Source | Units | Notes |
|--------------|-------------|------|--------|-------|-------|
| **date** | End-of-month date | Date | Derived | YYYY-MM-DD | Primary time index |
| **sentiment_michigan_ics** | University of Michigan Index of Consumer Sentiment | Numeric | FRED/Michigan Survey | Index (1966:Q1=100) | Monthly survey of ~500 households |
| **bullish_pct** | Percentage of AAII investors reporting bullish outlook | Numeric | AAII Sentiment Survey | Percentage (0-100) | Aggregated from weekly surveys via last-of-month |
| **neutral_pct** | Percentage of AAII investors reporting neutral outlook | Numeric | AAII Sentiment Survey | Percentage (0-100) | Aggregated from weekly surveys via last-of-month |
| **bearish_pct** | Percentage of AAII investors reporting bearish outlook | Numeric | AAII Sentiment Survey | Percentage (0-100) | Aggregated from weekly surveys via last-of-month |
| **bull_bear_spread** | Difference between bullish and bearish percentages | Numeric | AAII (Calculated) | Percentage Points | bull_bear_spread = bullish_pct - bearish_pct |
| **mkt_rf** | Market return in excess of risk-free rate | Numeric | Ken French Data Library | Percentage | Value-weighted market return minus RF |
| **smb** | Small Minus Big (Size factor) | Numeric | Ken French Data Library | Percentage | Return spread: small-cap minus large-cap stocks |
| **hml** | High Minus Low (Value factor) | Numeric | Ken French Data Library | Percentage | Return spread: high B/M minus low B/M stocks |
| **rf** | Risk-free rate | Numeric | Ken French Data Library | Percentage | One-month Treasury bill rate |
| **mkt_ret** | Total market return | Numeric | Ken French (Calculated) | Percentage | mkt_ret = mkt_rf + rf |
| **rmw** | Robust Minus Weak (Profitability factor) | Numeric | Ken French Data Library | Percentage | Return spread: high operating profitability minus low |
| **cma** | Conservative Minus Aggressive (Investment factor) | Numeric | Ken French Data Library | Percentage | Return spread: low investment firms minus high |

---

## Data Source Details

### Primary Data Sources

1. **Federal Reserve Economic Data (FRED)**
   - **Access Method**: FRED API (API Key: embedded in scripts)
   - **Series ID**: UMCSENT
   - **Frequency**: Monthly
   - **URL**: https://fred.stlouisfed.org/series/UMCSENT
   - **Variables**: sentiment_michigan_ics

2. **American Association of Individual Investors (AAII)**
   - **Access Method**: Manual download from member portal (Excel file)
   - **Original Frequency**: Weekly
   - **Aggregation Method**: Last week of each month
   - **URL**: https://www.aaii.com/sentimentsurvey
   - **Variables**: bullish_pct, neutral_pct, bearish_pct, bull_bear_spread

3. **Kenneth R. French Data Library**
   - **Access Method**: Automated download from website
   - **Files Downloaded**: 
     - Fama/French 3 Factors
     - Fama/French 5 Factors (2x3)
     - Momentum Factor
   - **URL**: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
   - **Variables**: mkt_rf, smb, hml, rf, mkt_ret, rmw, cma

---

## Cleaning Decisions Summary

### 1. **Date Alignment**
   - **Decision**: Normalize all sources to end-of-month dates
   - **Rationale**: Enables consistent temporal merging across datasets with different reporting frequencies
   - **Implementation**: 
     - FRED/French: Already end-of-month
     - AAII: Weekly data aggregated using last observation of each month

### 2. **AAII Weekly-to-Monthly Aggregation**
   - **Decision**: Use last weekly observation of each month (not average)
   - **Rationale**: Captures most recent investor sentiment at month-end; aligns with return measurement timing
   - **Impact**: Preserves sentiment volatility; avoids smoothing effects of averaging

### 3. **Decimal-to-Percentage Conversion (AAII)**
   - **Decision**: Multiply AAII sentiment values by 100
   - **Rationale**: Original Excel file stored percentages as decimals (0.35 instead of 35); standardize to percentage units
   - **Verification**: Ensured bullish_pct + neutral_pct + bearish_pct ≈ 100 for each observation

### 4. **Missing Values**
   - **Decision**: Filter all sources to 2004-2024 range
   - **Rationale**: All three sources have complete coverage for this period
   - **Result**: Zero missing values in final panel (252 complete observations)

### 5. **Merge Strategy**
   - **Decision**: Sequential left join on end-of-month date
   - **Sequence**: Michigan → AAII → French Factors
   - **Verification**: All joins resulted in zero dropped observations

### 6. **Outliers**
   - **Decision**: Retain all observations without winsorization
   - **Rationale**: Extreme sentiment values and market returns (e.g., 2008 financial crisis, 2020 pandemic) are economically meaningful
   - **Documentation**: Min/max values documented in summary statistics

---

## Variable Characteristics (Summary Statistics)

| Variable | N | Mean | Std Dev | Min | 25th | Median | 75th | Max |
|----------|---|------|---------|-----|------|--------|------|-----|
| sentiment_michigan_ics | 252 | 80.84 | 12.92 | 50.00 | 70.75 | 81.60 | 92.65 | 103.80 |
| bullish_pct | 252 | 36.45 | 8.49 | 16.44 | 30.39 | 35.75 | 41.96 | 57.66 |
| neutral_pct | 252 | 29.80 | 7.17 | 11.01 | 25.17 | 29.85 | 34.34 | 52.86 |
| bearish_pct | 252 | 33.75 | 9.40 | 15.00 | 26.29 | 32.60 | 40.60 | 60.81 |
| bull_bear_spread | 252 | 2.70 | 16.42 | -42.92 | -9.82 | 2.67 | 14.55 | 41.88 |
| mkt_rf | 252 | 0.81 | 4.39 | -17.20 | -1.75 | 1.31 | 3.26 | 13.60 |
| smb | 252 | -0.00 | 2.50 | -5.93 | -1.84 | -0.01 | 1.50 | 7.14 |
| hml | 252 | -0.06 | 3.15 | -13.83 | -1.75 | -0.23 | 1.43 | 12.86 |
| rf | 252 | 0.13 | 0.15 | 0.00 | 0.00 | 0.04 | 0.21 | 0.48 |
| mkt_ret | 252 | 0.94 | 4.39 | -17.12 | -1.58 | 1.40 | 3.55 | 13.60 |
| rmw | 252 | 0.36 | 1.88 | -4.78 | -0.78 | 0.34 | 1.32 | 7.19 |
| cma | 252 | -0.01 | 1.89 | -7.08 | -1.16 | -0.12 | 0.97 | 7.73 |

---

## Panel Structure

This dataset is structured as a **time-series panel** where:
- **Cross-sectional dimension**: None (single aggregate-level observation per time period)
- **Time dimension**: 252 months (2004-01 to 2024-12)
- **Format**: Long format (one row per time period)
- **Balanced**: Yes (no missing months)

**Note**: This is a pure time-series dataset aggregated at the market/economy level. It is ready for:
- Time-series regression analysis
- Granger causality tests
- VAR/VECM modeling
- Event studies around sentiment shifts

If entity-level analysis is required (e.g., individual stock returns), this dataset can serve as a supplementary source of market-level covariates to be merged with firm-level panels.

---

## Reproducibility

All data in this panel can be reproduced by running:

```bash
# Install dependencies
pip install -r requirements.txt

# Execute full pipeline
python code/run_all_fetch_scripts.py
```

**Script dependencies**:
- `code/fetch_michigan_sentiment.py` (requires FRED API key)
- `code/process_aaii_excel.py` (requires manual Excel file upload)
- `code/fetch_french_factors.py` (automated)
- `code/merge_final_panel.py` (merging logic)

---

## Data Quality Flags

- ✅ **No missing values**: All 252 observations complete
- ✅ **No duplicates**: Each month appears exactly once
- ✅ **Temporal consistency**: All dates are end-of-month
- ✅ **Logical consistency**: AAII percentages sum to ~100% (allowing for rounding)
- ✅ **Merge verification**: All three sources successfully merged on date key

---

## Usage Notes

### For Regression Analysis
- **Dependent variable candidates**: mkt_ret, mkt_rf (market returns)
- **Key independent variables**: sentiment_michigan_ics, bullish_pct, bearish_pct, bull_bear_spread
- **Control variables**: rf (interest rate environment), smb, hml, rmw, cma (factor exposures)

### Temporal Considerations
- **Autocorrelation**: Sentiment and return variables exhibit significant autocorrelation; consider HAC standard errors
- **Stationarity**: Test sentiment variables for unit roots before time-series modeling
- **Lags**: Consider lagged sentiment as predictors of future returns

### Ethical Considerations
- **Data loss**: None (full coverage 2004-2024 with zero missingness)
- **Survivorship bias**: Not applicable (market-level aggregates)
- **Selection bias**: Michigan Survey and AAII represent specific populations (consumers and individual investors); results may not generalize to institutional investors

---

## Citation

If using this dataset, please cite the original data sources:

**Michigan Sentiment**:
> University of Michigan: Surveys of Consumers (2024). Retrieved from FRED, Federal Reserve Bank of St. Louis; https://fred.stlouisfed.org/series/UMCSENT

**AAII Sentiment**:
> American Association of Individual Investors (AAII). (2024). AAII Investor Sentiment Survey. Retrieved from https://www.aaii.com/sentimentsurvey

**French Factors**:
> Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3-56.
> 
> Data: Kenneth R. French Data Library, https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

---

**Last Updated**: February 2026  
**Prepared by**: QM2023 Capstone - 2nd Row Team  
**Contact**: See repository documentation
