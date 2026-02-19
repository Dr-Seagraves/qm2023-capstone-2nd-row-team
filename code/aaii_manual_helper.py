"""
Helper Script to Manually Process AAII Sentiment Data
=====================================================

Since AAII's website has anti-bot protection, this script helps you
process manually downloaded data.

OPTION 1: Manual Copy-Paste from Website
-----------------------------------------
1. Go to: https://www.aaii.com/sentimentsurvey/sent_results
2. Select and copy the data table
3. Paste into Excel or Google Sheets
4. Save as: data/raw/aaii_sentiment.csv or .xlsx

OPTION 2: Check if data exists in data directory already
---------------------------------------------------------
Run this script to process any AAII data already in data/raw/

OPTION 3: Use Sample Instructions Below
-----------------------------------------
Follow the step-by-step guide to get historical data
"""

import pandas as pd
from pathlib import Path
from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR

def create_sample_instructions():
    """Create a template file showing expected format."""
    
    instructions_file = RAW_DATA_DIR / 'AAII_DOWNLOAD_INSTRUCTIONS.txt'
    
    instructions = """
================================================================================
HOW TO DOWNLOAD AAII SENTIMENT DATA
================================================================================

METHOD 1: From AAII Website (Best - Most Complete Data)
--------------------------------------------------------
1. Visit: https://www.aaii.com/sentimentsurvey/sent_results

2. You'll see a table with columns like:
   - Date (or Week Ending, or Reported Date)
   - Bullish (%)
   - Neutral (%)
   - Bearish (%)

3. Copy the entire table:
   - Click and drag to select all rows
   - Press Ctrl+C (Windows) or Cmd+C (Mac)

4. Paste into Excel or Google Sheets:
   - Open Excel or Google Sheets
   - Press Ctrl+V (Windows) or Cmd+V (Mac)
   - Data should appear in columns

5. Save the file:
   - In Excel: File > Save As
   - Format: CSV (Comma delimited) (*.csv)
   - Save to: data/raw/aaii_sentiment.csv
   
   OR
   
   - Format: Excel Workbook (*.xlsx)
   - Save to: data/raw/aaii_sentiment.xlsx

6. Run the processing script:
   python code/download_aaii_data.py


METHOD 2: From Historical Downloads (if available)
---------------------------------------------------
Some data aggregators provide AAII historical data:

A) Quandl/Nasdaq Data Link (may require API key):
   https://data.nasdaq.com/data/AAII/
   
B) Check your institutional access:
   - Bloomberg Terminal
   - FactSet
   - Refinitiv

C) Alternative sentiment data sources:
   - Investor Intelligence Survey
   - Market Vane
   - Sentix


Expected Data Format
--------------------
The final CSV should look like this:

Date,Bullish,Neutral,Bearish
2004-01-08,51.5,26.2,22.3
2004-01-15,49.2,28.3,22.5
...

Or with percent signs:

Date,Bullish %,Neutral %,Bearish %
2004-01-08,51.5%,26.2%,22.3%
2004-01-15,49.2%,28.3%,22.5%


Troubleshooting
---------------
If the script doesn't recognize your file:
1. Make sure the file is in data/raw/
2. Make sure it has a date column
3. Make sure it has Bullish, Neutral, Bearish columns
4. Column names don't have to be exact - the script will try to detect them

Questions?
----------
The script will automatically:
- Detect date columns
- Detect sentiment percentage columns  
- Remove % signs
- Convert to numeric values
- Filter to 2004-2024
- Aggregate weekly to monthly
- Calculate bull-bear spread

================================================================================
"""
    
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"✓ Created instructions file: {instructions_file}")
    return instructions

def check_for_existing_files():
    """Check if any AAII data files exist."""
    
    potential_files = [
        RAW_DATA_DIR / 'aaii_sentiment.csv',
        RAW_DATA_DIR / 'aaii_sentiment.xlsx',
        RAW_DATA_DIR / 'aaii_sentiment.xls',
        RAW_DATA_DIR / 'AAII_sentiment.csv',
        RAW_DATA_DIR / 'sent_results.csv',
        RAW_DATA_DIR / 'sentiment_survey.csv',
    ]
    
    found_files = [f for f in potential_files if f.exists()]
    
    return found_files

def main():
    print("\n" + "="*70)
    print("AAII SENTIMENT DATA - MANUAL DOWNLOAD HELPER")
    print("="*70)
    
    # Check for existing files
    existing = check_for_existing_files()
    
    if existing:
        print(f"\n✓ Found {len(existing)} potential AAII data file(s):")
        for f in existing:
            print(f"  - {f}")
        print("\nYou can process these by running:")
        print("  python code/download_aaii_data.py")
    else:
        print("\n✗ No AAII data files found in data/raw/")
        print("\nCreating download instructions...")
        instructions = create_sample_instructions()
        print("\n" + instructions)
        
        print("\nNext steps:")
        print("1. Follow the instructions above to download AAII data")
        print("2. Save the file to data/raw/aaii_sentiment.csv")
        print("3. Run: python code/download_aaii_data.py")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
