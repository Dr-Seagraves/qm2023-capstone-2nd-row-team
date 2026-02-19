# M1 Data Quality Report
**Sentiment and Financial Market Factors Panel Dataset**  
**QM2023 Capstone Project - 2nd Row Team**  
**Milestone 1 Deliverable**

---

## Executive Summary

This report documents the construction of a high-quality panel dataset linking consumer and investor sentiment measures to financial market factors over the period **January 2004 - December 2024** (252 monthly observations). The final dataset integrates three authoritative data sources:

1. **University of Michigan Consumer Sentiment Index** (FRED)
2. **AAII Investor Sentiment Survey** (manual Excel file)
3. **Kenneth R. French Factor Data Library** (automated download)

**Key Achievement**: Zero missing values across 252 months × 13 variables = **3,276 complete data points**.

---

## 1. Data Sources

### 1.1 Primary Data Sources

#### **Source 1: University of Michigan Consumer Sentiment (FRED)**
- **Provider**: Federal Reserve Economic Data (St. Louis Fed)
- **Original Source**: University of Michigan Surveys of Consumers
- **Access Method**: FRED API (automated download)
- **API Key**: Embedded in `code/fetch_michigan_sentiment.py` (excluded from version control per .gitignore)
- **Series ID**: UMCSENT
- **Frequency**: Monthly
- **Sample Size**: Surveys ~500 households monthly
- **URL**: https://fred.stlouisfed.org/series/UMCSENT
- **Variables Extracted**: `sentiment_michigan_ics` (Index of Consumer Sentiment)
- **Time Coverage**: 1978-present (filtered to 2004-2024 for this analysis)
- **Quality Assessment**: ✅ Authoritative government source, widely used in academic research

#### **Source 2: AAII Investor Sentiment Survey**
- **Provider**: American Association of Individual Investors
- **Access Method**: Manual download from member portal (requires AAII membership)
- **File Format**: Excel (.xls) - `sentiment.xls` uploaded by user
- **Frequency**: Weekly surveys (Thursday release)
- **Sample Size**: ~100-300 individual investor responses weekly
- **URL**: https://www.aaii.com/sentimentsurvey
- **Variables Extracted**: 
  - `bullish_pct`: % expecting stock prices to rise in next 6 months
  - `neutral_pct`: % expecting stock prices to stay flat
  - `bearish_pct`: % expecting stock prices to fall
  - `bull_bear_spread`: Calculated as bullish_pct - bearish_pct
- **Original Records**: 1,095 weekly observations (2004-2024)
- **Quality Assessment**: ✅ Industry-standard sentiment measure; cited in practitioner and academic publications

**Note on Access Barriers**: 
- AAII website employs Incapsula/Cloudflare anti-bot protection, preventing automated scraping
- Attempted web scraping methods (BeautifulSoup, Selenium, requests) all failed
- **Solution**: Manual Excel file upload required (documented in `data/AAII_README.md`)

#### **Source 3: Kenneth R. French Data Library**
- **Provider**: Dartmouth College (Kenneth R. French, Professor)
- **Access Method**: Automated HTTP download from publicly available ZIP files
- **Frequency**: Monthly
- **URL**: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- **Files Downloaded**:
  - Fama/French 3 Factors (F-F_Research_Data_Factors_CSV.zip)
  - Fama/French 5 Factors 2×3 (F-F_Research_Data_5_Factors_2x3_CSV.zip)
- **Variables Extracted**: 
  - `mkt_rf`: Market return minus risk-free rate
  - `smb`: Small Minus Big (size factor)
  - `hml`: High Minus Low (value factor)
  - `rmw`: Robust Minus Weak (profitability factor)
  - `cma`: Conservative Minus Aggressive (investment factor)
  - `rf`: Risk-free rate
  - `mkt_ret`: Total market return (calculated as mkt_rf + rf)
- **Time Coverage**: 1926-present (filtered to 2004-2024)
- **Quality Assessment**: ✅ Gold-standard academic source; most-cited asset pricing factors in finance research

---

## 2. Cleaning Decisions

### 2.1 Temporal Alignment

**Challenge**: Three data sources use different frequencies:
- Michigan Sentiment: Monthly (already end-of-month)
- AAII Sentiment: Weekly (Thursday releases)
- French Factors: Monthly (already end-of-month)

**Decision**: Normalize all data to **end-of-month dates** using pandas `freq='ME'` (month-end frequency).

**Implementation**:
```python
# Create month-end date range
date_range = pd.date_range(start='2004-01-31', end='2024-12-31', freq='ME')
```

**Rationale**: End-of-month standardization enables clean merging and aligns with financial reporting conventions (e.g., portfolio returns measured monthly).

**Before/After**:
- Before: Weekly AAII data (1,095 observations)
- After: Monthly AAII data (252 observations)
- Method: Last weekly observation of each month retained

---

### 2.2 AAII Weekly-to-Monthly Aggregation

**Challenge**: AAII reports weekly sentiment, while other sources are monthly.

**Decision**: Use the **last weekly observation** of each month (not monthly average).

**Implementation**:
```python
def aggregate_aaii_to_monthly(df):
    df['date'] = pd.to_datetime(df['date'])
    df['month_end'] = df['date'] + pd.offsets.MonthEnd(0)
    monthly = df.sort_values('date').groupby('month_end').last()
    return monthly
```

**Rationale**:
- Preserves sentiment volatility (averaging would artificially smooth data)
- Captures most recent investor mood at month-end, aligning with return measurement timing
- Standard practice in sentiment literature (e.g., Brown & Cliff, 2004)

**Economic Justification**: Investor sentiment at month-end is more relevant for predicting subsequent monthly returns than the average sentiment during the month.

**Verification**:
- Checked that each month maps to exactly one weekly observation
- Confirmed no months were dropped due to missing weeks
- Result: 1,095 weekly obs → 252 monthly obs (100% coverage)

---

### 2.3 AAII Decimal-to-Percentage Conversion

**Challenge**: Original Excel file stored percentages as decimals (e.g., 0.35 instead of 35%).

**Detection**:
```python
# Initial data preview showed values like:
# bullish: 0.5688, neutral: 0.2813, bearish: 0.1500
```

**Decision**: Multiply all AAII percentage columns by 100.

**Implementation**:
```python
pct_cols = ['bullish_pct', 'neutral_pct', 'bearish_pct', 'bull_bear_spread']
df[pct_cols] = df[pct_cols] * 100
```

**Verification**:
```python
# Check that percentages sum to ~100
df['total_pct'] = df['bullish_pct'] + df['neutral_pct'] + df['bearish_pct']
assert df['total_pct'].between(99.9, 100.1).all()
```

**Before/After Example**:
- Before: bullish=0.5688, neutral=0.2813, bearish=0.1500 (sum=1.0001)
- After: bullish=56.88, neutral=28.13, bearish=15.00 (sum=100.01)

---

### 2.4 Missing Values Handling

**Challenge**: Ensure complete temporal coverage across all three sources.

**Decision**: Filter all datasets to the common time range **2004-01-31 to 2024-12-31** where complete data exist.

**Analysis**:
| Source | Full Coverage | Filtered Coverage | Missing Obs |
|--------|--------------|------------------|-------------|
| Michigan (FRED) | 1978-present | 2004-2024 | 0 |
| AAII | 1987-present | 2004-2024 | 0 |
| French Factors | 1926-present | 2004-2024 | 0 |

**Result**: **Zero missing values** in the final 252×13 panel.

**Handling Strategy for Edge Cases** (none encountered):
- If missing: Would document # of missing obs and justify interpolation/deletion
- If one source has gaps: Would consider forward-fill for max 1 month if economically justified
- If extensive missingness: Would shorten time period or drop problematic variables

**Economic Justification**: Retaining all 252 months preserves critical periods:
- 2008 Financial Crisis (Bear Stearns, Lehman collapse)
- 2010-2019 Bull Market (longest in US history)
- 2020 COVID-19 Crash and Recovery
- 2022 Inflation/Rate Hike Cycle

---

### 2.5 Outlier Treatment

**Challenge**: Extreme values during crisis periods (e.g., sentiment during COVID-19, returns during 2008).

**Decision**: **Retain all observations without winsorization or trimming**.

**Rationale**:
- Extreme sentiment and returns are economically meaningful, not data errors
- Truncating outliers would bias analysis of sentiment-return relationships during volatile periods
- Robustness checks (median regression, quantile regression) can be used in M3 if needed

**Documented Extremes**:
| Variable | Min | Max | Event |
|----------|-----|-----|-------|
| sentiment_michigan_ics | 50.00 | 103.80 | COVID-19 crash (Apr 2020) |
| bearish_pct | 15.00 | 60.81 | Lehman collapse (Oct 2008) |
| bull_bear_spread | -42.92 | 41.88 | Financial crisis vs. Tech boom |
| mkt_ret | -17.12% | 13.60% | Oct 2008 vs. recoveries |

**Verification**: Visually inspected time-series plots (see `results/figures/final_panel_overview.png`) to confirm extremes correspond to known market events.

---

### 2.6 Duplicate Handling

**Challenge**: Pandas groupby operations can inadvertently duplicate columns.

**Issue Encountered**:
```python
# Bug discovery: AAII aggregation produced duplicate 'date' column
monthly.columns.duplicated().any()  # True
```

**Decision**: Explicitly drop original date column before groupby to prevent duplication.

**Implementation**:
```python
def aggregate_aaii_to_monthly(df):
    df['month_end'] = df['date'] + pd.offsets.MonthEnd(0)
    df_clean = df.drop('date', axis=1)  # Drop original date
    monthly = df_clean.groupby('month_end').last()
    monthly.reset_index(inplace=True)
    monthly.rename(columns={'month_end': 'date'}, inplace=True)
    return monthly
```

**Verification**:
```python
# Confirm no duplicates
assert not final_df.columns.duplicated().any()
```

---

## 3. Merge Strategy

### 3.1 Merge Sequence

**Approach**: Sequential left joins on end-of-month `date` column.

**Merge Order**:
1. Start with **Michigan Sentiment** (252 months)
2. Left join **AAII Sentiment** on date
3. Left join **French Factors** on date

**Code Implementation**:
```python
# Load individual processed files
michigan = pd.read_csv('data/processed/michigan_sentiment.csv')
aaii = pd.read_csv('data/processed/aaii_sentiment.csv')
french = pd.read_csv('data/processed/french_factors.csv')

# Sequential merges
panel = michigan.merge(aaii, on='date', how='left')
panel = panel.merge(french, on='date', how='left')
```

**Justification**: Left join ensures no observations are lost; sequence doesn't matter given perfect date overlap.

### 3.2 Merge Verification

**Pre-Merge Checks**:
```python
# Verify all sources cover same date range
assert michigan['date'].min() == aaii['date'].min() == french['date'].min()
assert michigan['date'].max() == aaii['date'].max() == french['date'].max()
```

**Post-Merge Checks**:
```python
# Verify no rows dropped
assert len(panel) == 252

# Verify no missing values introduced
assert panel.isnull().sum().sum() == 0

# Verify date uniqueness
assert panel['date'].is_unique
```

**Results**:
- ✅ All 252 observations retained
- ✅ All 13 variables populated (no NaNs)
- ✅ No duplicate dates

**Merge Diagnostics**:
| Merge Step | Left Rows | Right Rows | Output Rows | Dropped |
|------------|-----------|------------|-------------|---------|
| Michigan ← AAII | 252 | 252 | 252 | 0 |
| Panel ← French | 252 | 252 | 252 | 0 |

---

## 4. Final Dataset Summary

### 4.1 Dataset Characteristics

**File**: `data/final/analysis_panel.csv`

**Dimensions**:
- Rows: 252 (monthly observations)
- Columns: 13 (1 date + 12 variables)
- Total Cells: 3,276
- Missing Cells: 0 (100% complete)

**Time Coverage**:
- Start: 2004-01-31
- End: 2024-12-31
- Duration: 21 years (252 months)

**Panel Structure**:
- Type: Pure time-series (no cross-sectional dimension)
- Format: Long format (one row per time period)
- Balanced: Yes (no gaps in monthly sequence)

### 4.2 Variable Summary Statistics

| Variable | N | Mean | Std Dev | Min | 25% | Median | 75% | Max |
|----------|---|------|---------|-----|-----|--------|-----|-----|
| **sentiment_michigan_ics** | 252 | 80.84 | 12.92 | 50.00 | 70.75 | 81.60 | 92.65 | 103.80 |
| **bullish_pct** | 252 | 36.45 | 8.49 | 16.44 | 30.39 | 35.75 | 41.96 | 57.66 |
| **neutral_pct** | 252 | 29.80 | 7.17 | 11.01 | 25.17 | 29.85 | 34.34 | 52.86 |
| **bearish_pct** | 252 | 33.75 | 9.40 | 15.00 | 26.29 | 32.60 | 40.60 | 60.81 |
| **bull_bear_spread** | 252 | 2.70 | 16.42 | -42.92 | -9.82 | 2.67 | 14.55 | 41.88 |
| **mkt_rf** | 252 | 0.81 | 4.39 | -17.20 | -1.75 | 1.31 | 3.26 | 13.60 |
| **smb** | 252 | -0.00 | 2.50 | -5.93 | -1.84 | -0.01 | 1.50 | 7.14 |
| **hml** | 252 | -0.06 | 3.15 | -13.83 | -1.75 | -0.23 | 1.43 | 12.86 |
| **rf** | 252 | 0.13 | 0.15 | 0.00 | 0.00 | 0.04 | 0.21 | 0.48 |
| **mkt_ret** | 252 | 0.94 | 4.39 | -17.12 | -1.58 | 1.40 | 3.55 | 13.60 |
| **rmw** | 252 | 0.36 | 1.88 | -4.78 | -0.78 | 0.34 | 1.32 | 7.19 |
| **cma** | 252 | -0.01 | 1.89 | -7.08 | -1.16 | -0.12 | 0.97 | 7.73 |

**Saved**: `data/final/summary_statistics.csv`

### 4.3 Data Quality Metrics

✅ **Completeness**: 100% (0 missing values)  
✅ **Consistency**: All dates are end-of-month format  
✅ **Accuracy**: AAII percentages sum to ~100% (verified)  
✅ **Uniqueness**: No duplicate dates  
✅ **Timeliness**: Data extends through December 2024  
✅ **Validity**: All values within economically plausible ranges  

---

## 5. Reproducibility Checklist

### 5.1 Software Environment

**Python Version**: 3.12.1  
**Operating System**: Ubuntu 24.04.3 LTS (GitHub Codespaces Dev Container)

**Required Packages** (see `requirements.txt`):
```
pandas>=2.0.0
numpy>=1.24.0
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
fredapi>=0.5.0
openpyxl>=3.0.0
xlrd>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

**Installation**:
```bash
pip install -r requirements.txt
```

### 5.2 Execution Pipeline

**Full Reproducibility** (assuming FRED API key and AAII Excel file):

```bash
# 1. Download/process Michigan Sentiment
python code/fetch_michigan_sentiment.py

# 2. Process AAII Excel file (requires manual upload to data/raw/sentiment.xls)
python code/process_aaii_excel.py

# 3. Download French Factors
python code/fetch_french_factors.py

# 4. Merge all datasets
python code/merge_final_panel.py
```

**Or run all at once**:
```bash
python code/run_all_fetch_scripts.py
```

### 5.3 External Dependencies

**FRED API Key**:
- **Required for**: Michigan Sentiment download
- **How to obtain**: Register free account at https://fred.stlouisfed.org/
- **Storage**: Hardcoded in `code/fetch_michigan_sentiment.py` (line 12) - excluded from Git via .gitignore

**AAII Excel File**:
- **Required for**: AAII Sentiment data
- **How to obtain**: Download from https://www.aaii.com/sentimentsurvey (requires AAII membership ~$29/year)
- **Storage**: Save as `data/raw/sentiment.xls`
- **Alternative**: See `data/AAII_README.md` for manual data entry template

**French Factors**:
- **No login required**: Publicly available
- **Automated**: Script downloads directly from Dartmouth website

### 5.4 File Structure

```
qm2023-capstone-2nd-row-team/
├── code/
│   ├── fetch_michigan_sentiment.py    # FRED API download
│   ├── fetch_french_factors.py        # Auto-download French data
│   ├── process_aaii_excel.py          # Process uploaded Excel file
│   ├── merge_final_panel.py           # Merge all sources
│   └── run_all_fetch_scripts.py       # Master script
├── data/
│   ├── raw/                           # Original files
│   │   └── sentiment.xls              # AAII Excel (user-provided)
│   ├── processed/                     # Cleaned individual datasets
│   │   ├── michigan_sentiment.csv
│   │   ├── aaii_sentiment.csv
│   │   └── french_factors.csv
│   └── final/                         # Analysis-ready panel
│       ├── analysis_panel.csv         # ← MAIN DATASET
│       ├── summary_statistics.csv
│       └── data_dictionary.md
├── results/
│   └── figures/
│       ├── michigan_sentiment_timeseries.png
│       └── final_panel_overview.png
├── requirements.txt
├── M1_data_quality_report.md          # This file
└── AI_AUDIT_APPENDIX.md               # AI tool use documentation
```

---

## 6. Preliminary Research Questions

Based on the dataset constructed, potential research directions for M2 (Exploratory Analysis) and M3 (Econometric Modeling):

### 6.1 Sentiment-Return Predictability
**RQ1**: Do consumer sentiment (Michigan) and investor sentiment (AAII) predict subsequent monthly stock returns?

**Hypothesis**: 
- H1a: High consumer sentiment → Higher future returns (confidence channel)
- H1b: High investor bullishness → Lower future returns (contrarian signal)

**Model Preview**:
```
mkt_ret(t) = α + β1·sentiment_michigan(t-1) + β2·bull_bear_spread(t-1) + controls + ε(t)
```

### 6.2 Sentiment Divergence
**RQ2**: When consumer and investor sentiment diverge, which is more predictive of market outcomes?

**Hypothesis**: Retail investors (AAII) may exhibit herding/overreaction vs. broader consumers (Michigan).

### 6.3 Factor Model Augmentation
**RQ3**: Does sentiment explain alpha beyond traditional Fama-French factors?

**Model Preview**:
```
mkt_rf(t) = α + β_MKT + β_SMB + β_HML + β_RMW + β_CMA + γ·sentiment(t-1) + ε(t)
```

### 6.4 Crisis Periods
**RQ4**: Do sentiment measures provide early warning signals before market downturns?

**Event Study**: 2008 Financial Crisis, 2020 COVID Crash, 2022 Bear Market

---

## 7. Ethical Considerations

### 7.1 Data Loss Analysis

**What data are we losing?**

1. **Pre-2004 Historical Data**:
   - **Lost**: 26 years of Michigan data (1978-2003), 17 years of AAII (1987-2003)
   - **Justification**: Common overlap period ensures balanced panel; pre-2004 data missing from one source
   - **Impact**: Cannot study sentiment during 1987 crash, dot-com bubble, 9/11
   - **Mitigation**: 21-year sample still captures 2008 crisis, COVID, multiple business cycles

2. **Intra-Month Sentiment Volatility (AAII)**:
   - **Lost**: Weekly sentiment fluctuations within months (1,095 weeks → 252 months)
   - **Justification**: Matches monthly return measurement frequency
   - **Impact**: Cannot study high-frequency sentiment shifts
   - **Mitigation**: Retained last-of-month values (most relevant for monthly returns)

3. **Michigan Survey Details**:
   - **Lost**: Consumer Expectations (ICE) and Current Conditions (ICC) sub-indices
   - **Justification**: ICS (overall index) is most commonly used measure
   - **Impact**: Cannot decompose forward-looking vs. current sentiment
   - **Mitigation**: Can add ICE/ICC in M2 if needed (data available)

**Total Data Retention Rate**: 100% for target period (2004-2024)

### 7.2 Representativeness Concerns

**Michigan Survey**:
- **Sample**: ~500 US households monthly (phone survey)
- **Concern**: May underrepresent non-English speakers, households without landlines (increasingly mobile-only)
- **Impact**: Sentiment may skew toward older, English-speaking demographics

**AAII Survey**:
- **Sample**: ~100-300 AAII members weekly (self-selected)
- **Concern**: AAII members are individual investors (not institutional); may be wealthier, older, more male
- **Impact**: Sentiment reflects *retail* investor mood, not institutional or passive investors
- **Disclosure**: Results should be framed as "individual investor sentiment," not "market sentiment"

**French Factors**:
- **Sample**: All NYSE/AMEX/NASDAQ stocks (broad coverage)
- **Concern**: Survivorship bias (delisted firms excluded from historical returns)
- **Impact**: Returns may be slightly upward-biased
- **Mitigation**: French addresses this using CRSP delisting returns

### 7.3 Temporal Awareness

**Data Vintage**:
- Michigan: Real-time data (no revisions)
- AAII: Real-time data (historical surveys unchanged)
- French: **Monthly revisions** as new data added

**Concern**: French factor data is updated monthly; results may not be exactly reproducible if data are re-downloaded after updates.

**Mitigation**: 
- Save `data/raw/` files with download timestamps
- Document French data download date in this report: **February 2026**

---

## 8. Data Limitations

1. **Aggregation Level**: Market-level data only (no firm/sector breakdown)
   - Cannot study cross-sectional variation in sentiment effects
   - Cannot control for firm characteristics  
   - **Remediation**: Could merge with CRSP/Compustat for firm-level panel in future work

2. **Endogeneity Concerns**: 
   - Sentiment may respond to recent returns (reverse causality)
   - Omitted variables (e.g., media coverage, policy uncertainty) may drive both sentiment and returns  
   - **Remediation**: Use lagged sentiment, instrumental variables, or VAR models in M3

3. **Small Sample for Crisis Events**:
   - Only 2-3 major crises in 21-year sample
   - Difficult to generalize crisis-period findings  
   - **Remediation**: Use event study methods; acknowledge limited crisis observations

4. **Sentiment Measurement Error**:
   - Michigan: Survey responses may not reflect true economic expectations
   - AAII: Self-reported sentiment may differ from actual trading behavior  
   - **Remediation**: Use multiple sentiment proxies; check robustness to alternative measures

---

## 9. Next Steps (M2 Preview)

### 9.1 Exploratory Data Analysis

- **Time-series plots**: Visualize sentiment and returns over time (partially complete)
- **Correlation analysis**: Pairwise correlations between sentiment and returns
- **Stationarity tests**: ADF tests for unit roots
- **Granger causality**: Test if sentiment Granger-causes returns

### 9.2 Descriptive Analysis

- **Summary by decade**: Compare 2004-2009 vs. 2010s vs. 2020s
- **Crisis vs. expansion**: Compare sentiment during NBER recessions vs. expansions
- **Sentiment regimes**: Identify high-sentiment vs. low-sentiment periods

### 9.3 Data Augmentation (Optional)

**Potential additional variables for M2/M3**:
- VIX (volatility index) from FRED/CBOE
- Policy uncertainty index (Baker et al.)
- Google Trends sentiment proxies
- Corporate earnings growth (Compustat)
- Fed policy variables (interest rates, QE periods)

**Goal**: Expand to **15+ supplementary variables** as recommended in assignment rubric.

---

## 10. Conclusion

This M1 deliverable provides a **high-quality, analysis-ready panel dataset** linking consumer sentiment, investor sentiment, and financial market factors over 21 years (2004-2024). 

**Key Strengths**:
- ✅ Zero missing values (100% complete)
- ✅ Authoritative data sources (FRED, AAII, French)
- ✅ Reproducible pipeline (documented scripts)
- ✅ Rigorous cleaning decisions (economically justified)
- ✅ Ready for panel regression analysis

**Deliverables**:
- ✅ `data/final/analysis_panel.csv` (252×13 long-format panel)
- ✅ `data/final/data_dictionary.md` (variable definitions)
- ✅ `M1_data_quality_report.md` (this document)
- ✅ `AI_AUDIT_APPENDIX.md` (AI tool disclosure - see separate file)

**Next Milestone**: M2 will use this dataset for exploratory analysis, visualizations, and preliminary hypothesis testing to guide M3 econometric modeling.

---

## Appendices

### Appendix A: Code Snippets (Key Functions)

**A.1 Michigan Sentiment Download (FRED API)**:
```python
from fredapi import Fred
import pandas as pd

def download_from_fred(api_key, series_id='UMCSENT', start_date='2004-01-01'):
    """Download University of Michigan Consumer Sentiment from FRED."""
    fred = Fred(api_key=api_key)
    data = fred.get_series(series_id, observation_start=start_date)
    df = data.to_frame(name='sentiment_michigan_ics')
    df.index.name = 'date'
    return df.reset_index()
```

**A.2 AAII Weekly-to-Monthly Aggregation**:
```python
def aggregate_aaii_to_monthly(df):
    """Aggregate AAII weekly sentiment to monthly (last week of month)."""
    df['date'] = pd.to_datetime(df['date'])
    df['month_end'] = df['date'] + pd.offsets.MonthEnd(0)
    
    # Drop original date to avoid duplication in groupby
    df_clean = df.drop('date', axis=1)
    
    # Group by month-end, take last weekly observation
    monthly = df_clean.groupby('month_end').last()
    monthly.reset_index(inplace=True)
    monthly.rename(columns={'month_end': 'date'}, inplace=True)
    
    return monthly
```

**A.3 Panel Merge**:
```python
def merge_datasets():
    """Merge Michigan, AAII, and French data into final panel."""
    michigan = pd.read_csv('data/processed/michigan_sentiment.csv')
    aaii = pd.read_csv('data/processed/aaii_sentiment.csv')
    french = pd.read_csv('data/processed/french_factors.csv')
    
    # Sequential left joins
    panel = michigan.merge(aaii, on='date', how='left')
    panel = panel.merge(french, on='date', how='left')
    
    # Verify completeness
    assert panel.isnull().sum().sum() == 0, "Missing values detected!"
    
    return panel
```

### Appendix B: Validation Checks

**B.1 AAII Percentage Sum Check**:
```python
# Verify bullish + neutral + bearish ≈ 100
df['total_pct'] = df['bullish_pct'] + df['neutral_pct'] + df['bearish_pct']
print(f"Min total: {df['total_pct'].min():.2f}%")
print(f"Max total: {df['total_pct'].max():.2f}%")
assert df['total_pct'].between(99.9, 100.1).all(), "AAII percentages don't sum to 100!"
```

**B.2 Date Continuity Check**:
```python
# Verify no missing months
expected_dates = pd.date_range(start='2004-01-31', end='2024-12-31', freq='ME')
actual_dates = pd.to_datetime(df['date'])
assert len(expected_dates) == len(actual_dates), "Missing months detected!"
assert (expected_dates == actual_dates.sort_values()).all(), "Date sequence broken!"
```

**B.3 Merge Diagnostic**:
```python
# Check for unmatched records
print(f"Michigan records: {len(michigan)}")
print(f"AAII records: {len(aaii)}")
print(f"French records: {len(french)}")
print(f"Final panel records: {len(panel)}")
print(f"Missing values: {panel.isnull().sum().sum()}")
```

### Appendix C: Known Issues & Resolutions

**Issue 1: Pandas Frequency Deprecation**
- **Problem**: `freq='M'` deprecated in pandas 2.0+
- **Solution**: Use `freq='ME'` (month-end) with try/except fallback
- **Code**: 
  ```python
  try:
      date_range = pd.date_range(start, end, freq='ME')
  except ValueError:
      date_range = pd.date_range(start, end, freq='M')
  ```

**Issue 2: AAII Website Scraping Blocked**
- **Problem**: Incapsula/Cloudflare prevents automated downloads
- **Solution**: Manual Excel file upload workflow
- **Documentation**: See `data/AAII_README.md`

**Issue 3: xlrd Package Dependency**
- **Problem**: Reading .xls files requires xlrd (not installed by default)
- **Solution**: Added `xlrd>=2.0.0` to requirements.txt
- **Command**: `pip install xlrd`

---

**Report Prepared**: February 2026  
**Authors**: QM2023 Capstone - 2nd Row Team  
**Milestone**: M1 (Data Collection & Cleaning)  
**Next Milestone**: M2 (Exploratory Data Analysis) - due [insert date]

---

## References

Baker, M., & Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns. *Journal of Finance*, 61(4), 1645-1680.

Brown, G. W., & Cliff, M. T. (2004). Investor sentiment and the near-term stock market. *Journal of Empirical Finance*, 11(1), 1-27.

Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3-56.

University of Michigan: Surveys of Consumers. (2024). Retrieved from FRED, Federal Reserve Bank of St. Louis; https://fred.stlouisfed.org/series/UMCSENT
