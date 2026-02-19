# Data Pipeline Documentation

This directory contains the data pipeline for the capstone project, collecting sentiment and market factor data from 2004-2024.

## Data Sources

### 1. University of Michigan Consumer Sentiment
- **URL**: https://data.sca.isr.umich.edu/data-archive/mine.php
- **Script**: `code/fetch_michigan_sentiment.py`
- **Frequency**: Monthly
- **Variables**: Index of Consumer Sentiment (ICS), Consumer Expectations (ICE), Current Conditions (ICC)
- **Access**: Requires subscription (or use FRED alternative)

### 2. AAII Investor Sentiment Survey
- **URL**: https://www.aaii.com/sentimentsurvey
- **Script**: `code/fetch_aaii_sentiment.py`
- **Frequency**: Weekly (aggregated to monthly)
- **Variables**: Bullish %, Bearish %, Neutral %, Bull-Bear Spread
- **Access**: Requires AAII membership for historical data

### 3. Kenneth French Data Library
- **URL**: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- **Script**: `code/fetch_french_factors.py`
- **Frequency**: Monthly
- **Variables**: Market return, SMB, HML, Momentum, Risk-free rate, (optional: RMW, CMA)
- **Access**: Publicly available

## Directory Structure

```
data/
├── raw/              # Original downloaded files
├── processed/        # Cleaned individual datasets
│   ├── michigan_sentiment.csv
│   ├── aaii_sentiment.csv
│   └── french_factors.csv
└── final/           # Merged analysis panel
    ├── analysis_panel.csv
    └── summary_statistics.csv
```

## Usage

### Option 1: Run All Scripts Together
```bash
# Install dependencies
pip install -r requirements.txt

# Run complete pipeline
python code/run_all_fetch_scripts.py
```

### Option 2: Run Scripts Individually
```bash
# Fetch/process each dataset
python code/fetch_michigan_sentiment.py
python code/fetch_aaii_sentiment.py
python code/fetch_french_factors.py

# Merge into final panel
python code/merge_final_panel.py
```

## Manual Download Instructions

### For Michigan Sentiment Data:
1. Visit https://data.sca.isr.umich.edu/data-archive/mine.php
2. Log in with institutional credentials
3. Download the Index of Consumer Sentiment monthly data
4. Save as: `data/raw/michigan_consumer_sentiment.csv`

**Alternative (Public Access)**:
- Download from FRED: https://fred.stlouisfed.org/series/UMCSENT
- The script can automatically use FRED as fallback

### For AAII Sentiment Data:
1. Visit https://www.aaii.com/sentimentsurvey
2. Log in with AAII membership
3. Download historical sentiment survey data
4. Save as: `data/raw/aaii_sentiment.csv`

**Alternative**:
- Manually collect recent weeks from public tables
- Check if your institution has access through Bloomberg or similar

### For French Factor Data:
No manual download needed - the script automatically downloads from Ken French's website.

## Output Dataset Structure

The final panel (`data/final/analysis_panel.csv`) contains:

| Column | Description | Source |
|--------|-------------|--------|
| date | End-of-month date | - |
| sentiment_michigan_ics | Consumer Sentiment Index | Michigan |
| sentiment_michigan_ice | Consumer Expectations | Michigan |
| sentiment_michigan_icc | Current Conditions | Michigan |
| bullish_pct | % Bullish investors | AAII |
| bearish_pct | % Bearish investors | AAII |
| neutral_pct | % Neutral investors | AAII |
| bull_bear_spread | Bullish % - Bearish % | AAII |
| mkt_rf | Market excess return | French |
| smb | Size factor | French |
| hml | Value factor | French |
| rf | Risk-free rate | French |
| mkt_ret | Total market return | French |
| mom | Momentum factor | French |

## Data Quality Notes

- **Time Period**: 2004-2024 (252 months)
- **Missing Values**: Handled via left join on complete monthly date range
- **Frequency Alignment**: AAII weekly data aggregated to monthly (last week of month)
- **Date Format**: All dates standardized to end-of-month

## Troubleshooting

### "File not found" errors
- Download the data manually following instructions above
- Check that files are saved in `data/raw/` directory

### Import errors
- Run: `pip install -r requirements.txt`
- Ensure you're in the project root directory

### Internet connection issues
- French data download requires stable connection
- Consider downloading manually if automated fetch fails

## Citation

If using this data in your research, please cite:

- **Michigan**: University of Michigan Survey of Consumers
- **AAII**: American Association of Individual Investors Sentiment Survey
- **French**: Kenneth R. French Data Library

## Contact

For questions about the data pipeline, contact the project team or refer to the main README.md.
