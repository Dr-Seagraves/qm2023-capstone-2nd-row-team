"""
Fetch and Process AAII Investor Sentiment Survey Data
=====================================================

Downloads investor sentiment data from AAII Sentiment Survey.
Data period: 2004-2024
Output: data/processed/aaii_sentiment.csv

Note: AAII historical data requires membership for full access.
This script provides options for both members and non-members.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR

# ==============================================================================
# CONFIGURATION
# ==============================================================================

START_YEAR = 2004
END_YEAR = 2024

AAII_URL = "https://www.aaii.com/sentimentsurvey/sent_results"

# ==============================================================================
# DATA DOWNLOAD FUNCTIONS
# ==============================================================================

def download_aaii_data():
    """
    Download AAII Sentiment Survey data.
    
    NOTE: Full historical data requires AAII membership.
    
    Instructions for members:
    1. Go to https://www.aaii.com/sentimentsurvey
    2. Log in to your AAII account
    3. Navigate to Historical Data section
    4. Download the CSV or Excel file with weekly sentiment data
    5. Save it as: data/raw/aaii_sentiment.csv or .xlsx
    
    For non-members:
    - You can manually copy recent data from the public table
    - Or use alternative sources like Quandl/Alpha Vantage if you have API access
    
    Returns:
        pd.DataFrame: Raw AAII sentiment data
    """
    # Check for raw data files
    raw_file_csv = RAW_DATA_DIR / 'aaii_sentiment.csv'
    raw_file_xlsx = RAW_DATA_DIR / 'aaii_sentiment.xlsx'
    
    if raw_file_csv.exists():
        print(f"✓ Found raw data: {raw_file_csv}")
        df = pd.read_csv(raw_file_csv)
    elif raw_file_xlsx.exists():
        print(f"✓ Found raw data: {raw_file_xlsx}")
        df = pd.read_excel(raw_file_xlsx)
    else:
        print("\n" + "="*70)
        print("MANUAL DOWNLOAD REQUIRED")
        print("="*70)
        print("\nAAII historical data requires membership access.")
        print("Please follow these steps:\n")
        print("OPTION 1 - For AAII Members:")
        print("1. Visit: https://www.aaii.com/sentimentsurvey")
        print("2. Log in with your credentials")
        print("3. Download historical sentiment data (CSV/Excel)")
        print("4. Save the file as:")
        print(f"   {raw_file_csv}")
        print("\nOPTION 2 - Alternative Data Sources:")
        print("- Quandl: https://www.quandl.com/data/AAII/")
        print("- Yahoo Finance (limited history)")
        print("- Manual entry from public weekly reports")
        print("="*70)
        raise FileNotFoundError(f"Raw data file not found. Please download manually.")
    
    return df

def scrape_aaii_recent():
    """
    Attempt to scrape recent AAII data from public webpage.
    This only gets the most recent few weeks of data.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        print("Attempting to fetch recent AAII data from public page...")
        
        # Note: This URL may change; update as needed
        url = "https://www.aaii.com/sentimentsurvey"
        
        # You may need to handle authentication here if required
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the sentiment table (this selector may need adjustment)
        # AAII structure changes, so this is a template
        table = soup.find('table', {'class': 'sentiment-table'})
        
        if table:
            df = pd.read_html(str(table))[0]
            print(f"✓ Scraped {len(df)} recent records")
            return df
        else:
            print("Could not find sentiment table on page")
            return None
            
    except ImportError:
        print("Required packages not installed: pip install requests beautifulsoup4 lxml")
        return None
    except Exception as e:
        print(f"Error scraping AAII data: {e}")
        return None

# ==============================================================================
# DATA PROCESSING FUNCTIONS
# ==============================================================================

def process_aaii_data(df):
    """
    Clean and standardize AAII sentiment data.
    
    Expected columns (will auto-detect):
    - Date/Week Ending
    - Bullish % 
    - Neutral %
    - Bearish %
    
    Args:
        df: Raw AAII dataframe
        
    Returns:
        pd.DataFrame: Processed sentiment data
    """
    df_clean = df.copy()
    
    # Detect and standardize date column
    date_cols = [col for col in df_clean.columns 
                 if any(x in str(col).lower() for x in ['date', 'week', 'time', 'period'])]
    
    if date_cols:
        date_col = date_cols[0]
        df_clean['date'] = pd.to_datetime(df_clean[date_col])
    else:
        # Try to parse index
        try:
            df_clean['date'] = pd.to_datetime(df_clean.index)
        except:
            raise ValueError("Could not identify date column")
    
    # Detect sentiment columns
    column_mapping = {}
    
    # Look for bullish percentage
    bullish_cols = [col for col in df_clean.columns 
                    if 'bull' in str(col).lower() and '%' in str(col)]
    if bullish_cols:
        column_mapping[bullish_cols[0]] = 'bullish_pct'
    
    # Look for bearish percentage
    bearish_cols = [col for col in df_clean.columns 
                    if 'bear' in str(col).lower() and '%' in str(col)]
    if bearish_cols:
        column_mapping[bearish_cols[0]] = 'bearish_pct'
    
    # Look for neutral percentage
    neutral_cols = [col for col in df_clean.columns 
                    if 'neutral' in str(col).lower() and '%' in str(col)]
    if neutral_cols:
        column_mapping[neutral_cols[0]] = 'neutral_pct'
    
    # Rename columns
    df_clean = df_clean.rename(columns=column_mapping)
    
    # Select relevant columns
    output_cols = ['date']
    for col in ['bullish_pct', 'neutral_pct', 'bearish_pct']:
        if col in df_clean.columns:
            output_cols.append(col)
    
    df_clean = df_clean[output_cols].copy()
    
    # Clean percentage values (remove % signs if present, convert to float)
    for col in ['bullish_pct', 'neutral_pct', 'bearish_pct']:
        if col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].astype(str).str.replace('%', '').astype(float)
    
    # Calculate bull-bear spread (a common sentiment indicator)
    if 'bullish_pct' in df_clean.columns and 'bearish_pct' in df_clean.columns:
        df_clean['bull_bear_spread'] = df_clean['bullish_pct'] - df_clean['bearish_pct']
    
    # Filter date range
    df_clean = df_clean[
        (df_clean['date'].dt.year >= START_YEAR) & 
        (df_clean['date'].dt.year <= END_YEAR)
    ]
    
    # Sort by date
    df_clean = df_clean.sort_values('date').reset_index(drop=True)
    
    # Remove duplicates
    df_clean = df_clean.drop_duplicates(subset=['date'], keep='last')
    
    return df_clean

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("AAII INVESTOR SENTIMENT SURVEY DATA PIPELINE")
    print("="*70)
    print(f"Period: {START_YEAR}-{END_YEAR}")
    print(f"Output: {PROCESSED_DATA_DIR / 'aaii_sentiment.csv'}\n")
    
    # Step 1: Download/Load Data
    print("[Step 1/3] Loading data...")
    try:
        df_raw = download_aaii_data()
    except FileNotFoundError:
        print("\nAttempting to scrape recent data...")
        df_raw = scrape_aaii_recent()
        if df_raw is None or len(df_raw) == 0:
            print("\n✗ Could not obtain AAII data.")
            print("Please download the data manually and try again.")
            return
    
    print(f"✓ Loaded {len(df_raw)} raw records")
    print(f"  Columns found: {list(df_raw.columns)}")
    
    # Step 2: Process Data
    print("\n[Step 2/3] Processing and cleaning data...")
    df_processed = process_aaii_data(df_raw)
    print(f"✓ Processed {len(df_processed)} records")
    print(f"  Date range: {df_processed['date'].min()} to {df_processed['date'].max()}")
    print(f"  Columns: {list(df_processed.columns)}")
    
    # Check data quality
    if len(df_processed) < 52:  # Less than one year of weekly data
        print("\n⚠ Warning: Dataset seems small. You may want to verify data completeness.")
    
    # Step 3: Save Processed Data
    print("\n[Step 3/3] Saving processed data...")
    output_file = PROCESSED_DATA_DIR / 'aaii_sentiment.csv'
    df_processed.to_csv(output_file, index=False)
    print(f"✓ Saved to: {output_file}")
    
    # Summary statistics
    print("\n" + "="*70)
    print("DATA SUMMARY")
    print("="*70)
    print(df_processed.describe())
    
    print("\n" + "="*70)
    print("✓ AAII sentiment data processing complete!")
    print("="*70)

if __name__ == "__main__":
    main()
