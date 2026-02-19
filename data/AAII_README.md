# AAII Sentiment Survey Data Collection Guide

## Overview

The AAII (American Association of Individual Investors) Sentiment Survey tracks investor sentiment through weekly surveys. Unfortunately, the website has anti-bot protection that prevents automated downloads.

## ✅ What We've Created For You

1. **[download_aaii_data.py](../code/download_aaii_data.py)** - Automated download attempt + manual data processor
2. **[aaii_manual_helper.py](../code/aaii_manual_helper.py)** - Instructions and helper utilities
3. **[AAII_DOWNLOAD_INSTRUCTIONS.txt](AAII_DOWNLOAD_INSTRUCTIONS.txt)** - Step-by-step download guide

## 📥 How to Get AAII Data

### Method 1: Manual Download from AAII Website (Recommended)

**Step 1:** Visit the AAII Sentiment Survey results page:
```
https://www.aaii.com/sentimentsurvey/sent_results
```

**Step 2:** On the page, you'll see a table with columns:
- Date/Week Ending/Reported Date
- Bullish (%)
- Neutral (%)
- Bearish (%)

**Step 3:** Copy the data table:
- Select all rows in the table (click and drag, or Ctrl+A)
- Copy (Ctrl+C or Cmd+C)

**Step 4:** Paste into spreadsheet:
- Open Excel, Google Sheets, or any spreadsheet application
- Paste the data (Ctrl+V or Cmd+V)
- The data should arrange itself into columns

**Step 5:** Save as CSV or Excel:
- **CSV**: File > Save As > Choose "CSV (Comma delimited) (*.csv)"
- **Excel**: File > Save As > Choose "Excel Workbook (*.xlsx)"
- **Save location**: `data/raw/aaii_sentiment.csv` or `.xlsx`

**Step 6:** Process the data:
```bash
python code/download_aaii_data.py
```

### Method 2: From Data Providers (If You Have Access)

**A. Nasdaq Data Link (formerly Quandl)**
- URL: https://data.nasdaq.com/data/AAII/
- Requires API key (free tier available)
- Has historical AAII sentiment data

**B. Institutional Access**
- Bloomberg Terminal: `AAIIBULL <Index>`, `AAIIBEAR <Index>`
- FactSet
- Refinitiv/Eikon

**C. Financial APIs**
- Some paid financial data APIs include AAII sentiment

### Method 3: Alternative Sentiment Indicators

If AAII data is unavailable, consider these alternatives:
- **Investor Intelligence** - Similar investor sentiment survey
- **Market Vane** - Commodity trader sentiment
- **CNN Fear & Greed Index** - Composite sentiment measure
- **VIX** - Market volatility (fear) index
- **Put/Call Ratio** - Options market sentiment

## 📊 Expected Data Format

Your manually downloaded file should have these columns:

```csv
Date,Bullish,Neutral,Bearish
2004-01-08,51.5,26.2,22.3
2004-01-15,49.2,28.3,22.5
2004-01-22,48.7,29.1,22.2
...
```

Or with percent signs (the script handles both):

```csv
Date,Bullish %,Neutral %,Bearish %
2004-01-08,51.5%,26.2%,22.3%
2004-01-15,49.2%,28.3%,22.5%
```

**Important:** 
- Column names can vary - the script auto-detects them
- Data frequency: Weekly is ideal (will be aggregated to monthly)
- Date format: Most common formats are automatically recognized

## 🔧 Processing Script Features

The `download_aaii_data.py` script will automatically:

1. ✅ Detect date columns (various formats)
2. ✅ Detect sentiment columns (handles "Bullish %", "Bullish", etc.)
3. ✅ Remove % signs if present
4. ✅ Convert to numeric values
5. ✅ Filter to 2004-2024 date range
6. ✅ Handle weekly data (most recent week per month)
7. ✅ Calculate bull-bear spread
8. ✅ Remove duplicates
9. ✅ Save to `data/processed/aaii_sentiment.csv`

## 📁 File Locations

**Save your downloaded file to:**
```
data/raw/aaii_sentiment.csv      (CSV format - recommended)
data/raw/aaii_sentiment.xlsx     (Excel format - also works)
```

**Processed output will be saved to:**
```
data/processed/aaii_sentiment.csv
```

## 🚀 Quick Start

```bash
# 1. Download data manually from AAII website
# 2. Save to data/raw/aaii_sentiment.csv
# 3. Run processing script:
python code/download_aaii_data.py

# 4. Verify output:
head data/processed/aaii_sentiment.csv
```

## ⚠️ Troubleshooting

### "Could not identify date column"
- Make sure your CSV has a column with dates
- Common names: "Date", "Week Ending", "Reported Date"
- The script looks for these automatically

### "No data in date range"
- Verify your data includes years 2004-2024
- Check date format is recognizable (YYYY-MM-DD, MM/DD/YYYY, etc.)

### "File not found"
- Ensure file is saved exactly as: `data/raw/aaii_sentiment.csv`
- Check file extension (.csv vs .xlsx)
- Verify you're in the project root directory

### Script runs but no output
- Check if data was saved to `data/processed/aaii_sentiment.csv`
- Review console output for error messages
- Verify input file has data (not empty)

## 📈 What Happens Next

Once you have AAII data processed:

1. You'll have three datasets ready:
   - ✅ French Factors (automated)
   - ✅ Michigan Sentiment (automated with FRED key)
   - ✅ AAII Sentiment (manual download)

2. Run the merge script:
```bash
python code/merge_final_panel.py
```

3. Your final analysis panel will be at:
```
data/final/analysis_panel.csv
```

## 💡 Tips

- **Weekly data is fine**: The script aggregates to monthly automatically
- **More data is better**: Try to get data back to at least 2004
- **Export the whole table**: Don't filter by date before downloading
- **Save raw data**: Keep your original download in `data/raw/`

## 📞 Need Help?

If you encounter issues:

1. Run the helper script for detailed instructions:
```bash
python code/aaii_manual_helper.py
```

2. Check the instructions file:
```bash
cat data/raw/AAII_DOWNLOAD_INSTRUCTIONS.txt
```

3. Verify file format by previewing:
```bash
head -20 data/raw/aaii_sentiment.csv
```

---

**Last Updated:** February 19, 2026  
**Status:** Manual download required due to website anti-bot protection
