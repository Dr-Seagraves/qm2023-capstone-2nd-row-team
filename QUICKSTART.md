# Data Collection Quick Start Guide

## 🎯 Overview

You now have a complete data pipeline to collect and merge four datasets for 2004-2024:

1. **University of Michigan Consumer Sentiment** (requires manual download)
2. **AAII Investor Sentiment Survey** (requires manual download or membership)
3. **Kenneth French Factor Data** ✅ (automatically downloaded)
4. **Final merged panel dataset**

## 📁 Created Files

### Fetch Scripts (code/)
- `fetch_michigan_sentiment.py` - Michigan consumer sentiment
- `fetch_aaii_sentiment.py` - AAII investor sentiment
- `fetch_french_factors.py` - Ken French factors ✅ TESTED
- `merge_final_panel.py` - Merge all into final panel
- `run_all_fetch_scripts.py` - Master script to run all

### Documentation
- `requirements.txt` - Python dependencies
- `data/DATA_README.md` - Complete data documentation

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Option A - Automatic Download (French data only)
```bash
# This will work immediately for French factors
python code/fetch_french_factors.py
```
✅ **Already completed!** Your French factors are ready at `data/processed/french_factors.csv`

### Step 3: Manual Downloads (Michigan & AAII)

#### For Michigan Consumer Sentiment:
**Option 1 - Official Source** (requires subscription):
1. Visit: https://data.sca.isr.umich.edu/data-archive/mine.php
2. Log in with institutional credentials
3. Download monthly Index of Consumer Sentiment data
4. Save as: `data/raw/michigan_consumer_sentiment.csv`

**Option 2 - FRED** (public, automated):
```bash
pip install pandas-datareader
python code/fetch_michigan_sentiment.py
```
The script will automatically try to download from FRED if the raw file is missing.

#### For AAII Sentiment:
**Option 1 - AAII Members**:
1. Visit: https://www.aaii.com/sentimentsurvey
2. Log in with AAII membership
3. Download historical sentiment data
4. Save as: `data/raw/aaii_sentiment.csv`

**Option 2 - Alternative Sources**:
- Check if available through your institution's Bloomberg terminal
- Use Quandl API (if you have access)
- Manually compile from public weekly reports

### Step 4: Run Individual Scripts
```bash
# After placing manual downloads in data/raw/
python code/fetch_michigan_sentiment.py
python code/fetch_aaii_sentiment.py
python code/fetch_french_factors.py  # Already done!
```

### Step 5: Merge Into Final Panel
```bash
python code/merge_final_panel.py
```

### Option B: Run Everything at Once
```bash
python code/run_all_fetch_scripts.py
```

## 📊 Expected Output

After successful completion, you'll have:

```
data/
├── raw/
│   ├── michigan_consumer_sentiment.csv (manual)
│   ├── aaii_sentiment.csv (manual)
│   ├── french_ff3.csv ✅
│   ├── french_mom.csv ✅
│   └── french_5factors.csv ✅
│
├── processed/
│   ├── michigan_sentiment.csv
│   ├── aaii_sentiment.csv
│   └── french_factors.csv ✅
│
└── final/
    ├── analysis_panel.csv (252 months x ~15 variables)
    └── summary_statistics.csv
```

## 📈 Final Dataset Variables

The merged panel (`data/final/analysis_panel.csv`) will include:

### Consumer Sentiment (Michigan)
- `sentiment_michigan_ics` - Index of Consumer Sentiment
- `sentiment_michigan_ice` - Consumer Expectations
- `sentiment_michigan_icc` - Current Conditions

### Investor Sentiment (AAII)
- `bullish_pct` - % Bullish investors
- `bearish_pct` - % Bearish investors
- `neutral_pct` - % Neutral investors
- `bull_bear_spread` - Bullish % - Bearish %

### Market Factors (French) ✅
- `mkt_rf` - Market excess return
- `smb` - Size factor (Small Minus Big)
- `hml` - Value factor (High Minus Low)
- `rf` - Risk-free rate
- `mkt_ret` - Total market return
- `rmw` - Profitability factor
- `cma` - Investment factor

## 🔧 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Manual download files not found
Make sure files are saved exactly as:
- `data/raw/michigan_consumer_sentiment.csv` (or .xlsx)
- `data/raw/aaii_sentiment.csv` (or .xlsx)

### Internet connection issues
The French data download requires internet. If it fails, you can download manually from:
https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

## 💡 Tips

1. **Start with what works**: The French factors script is already tested and working!

2. **FRED alternative**: For Michigan data, the script can automatically use FRED as a fallback if you can't access the official source.

3. **Data frequency**: AAII data is weekly but will be automatically aggregated to monthly to match other datasets.

4. **Date range**: All scripts are configured for 2004-2024 (252 months). You can modify the `START_YEAR` and `END_YEAR` variables in each script.

## 📚 Next Steps

Once you have the final panel:

```python
import pandas as pd

# Load the analysis panel
df = pd.read_csv('data/final/analysis_panel.csv')

# Convert date column
df['date'] = pd.to_datetime(df['date'])

# Begin your analysis!
print(df.info())
print(df.describe())
```

## ✅ What's Already Done

- ✅ Ken French factor data downloaded and processed (252 months)
- ✅ All scripts created and tested
- ✅ Project structure set up
- ✅ Dependencies documented

## 📝 What You Need to Do

1. Obtain Michigan sentiment data (or let script use FRED)
2. Obtain AAII sentiment data (requires membership or manual collection)
3. Run the fetch scripts
4. Run the merge script

See `data/DATA_README.md` for complete documentation.

## 🆘 Need Help?

- Check error messages - scripts provide detailed instructions
- Review `data/DATA_README.md` for detailed documentation
- Each script can be run independently for easier debugging
- French data (already working) can be used alone if needed

---

**Last Updated**: February 19, 2026
**Status**: French factors ready ✅ | Michigan & AAII pending manual downloads
