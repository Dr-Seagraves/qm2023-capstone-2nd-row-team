"""
Fetch and Process University of Michigan Consumer Sentiment Data
================================================================

Downloads consumer sentiment data from U of M Survey of Consumers.
Data period: 2004-2024
Output: data/processed/michigan_sentiment.csv

Note: The University of Michigan data requires subscription access.
This script provides two modes:
1. Manual download: Download CSV from their website and place in data/raw/
2. Automated: If you have API access, configure credentials below
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

# FRED API Key for automatic download
FRED_API_KEY = "50023fd424a7ec3070a97a36dc325fab"

# ==============================================================================
# DATA DOWNLOAD FUNCTIONS
# ==============================================================================

def download_michigan_data():
    """
    Download Michigan Consumer Sentiment data.
    
    NOTE: The Michigan Survey data requires subscription.
    
    Instructions:
    1. Go to https://data.sca.isr.umich.edu/data-archive/mine.php
    2. Log in with your credentials
    3. Download the monthly data file (Excel or CSV)
    4. Save it as: data/raw/michigan_consumer_sentiment.csv
    
    Returns:
        pd.DataFrame: Raw sentiment data
    """
    # Check if raw data file exists
    raw_file_csv = RAW_DATA_DIR / 'michigan_consumer_sentiment.csv'
    raw_file_xlsx = RAW_DATA_DIR / 'michigan_consumer_sentiment.xlsx'
    
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
        print("\nThe University of Michigan Consumer Sentiment data requires")
        print("subscription access. Please follow these steps:\n")
        print("1. Visit: https://data.sca.isr.umich.edu/data-archive/mine.php")
        print("2. Log in with institutional credentials")
        print("3. Download the Index of Consumer Sentiment (ICS) monthly data")
        print("4. Save the file as:")
        print(f"   {raw_file_csv}")
        print("\nAlternatively, you can use the publicly available summary data")
        print("from FRED (Federal Reserve Economic Data):")
        print("   https://fred.stlouisfed.org/series/UMCSENT")
        print("="*70)
        raise FileNotFoundError(f"Raw data file not found. Please download manually.")
    
    return df

def download_from_fred():
    """
    Download Michigan sentiment from FRED (Federal Reserve Economic Data).
    This is the primary automated download method.
    
    Downloads three main indices:
    - UMCSENT: Index of Consumer Sentiment (ICS)
    - UMCSENT: Consumer Sentiment (overall measure)
    - Additional indices if available
    
    Returns:
        pd.DataFrame: Michigan sentiment data
    """
    try:
        from fredapi import Fred
        
        print("Downloading Michigan sentiment data from FRED...")
        print(f"  Period: {START_YEAR}-{END_YEAR}")
        
        # Initialize FRED API
        fred = Fred(api_key=FRED_API_KEY)
        
        # Download Index of Consumer Sentiment (main index)
        print("  Fetching Index of Consumer Sentiment (UMCSENT)...")
        ics = fred.get_series('UMCSENT', 
                              observation_start=f'{START_YEAR}-01-01',
                              observation_end=f'{END_YEAR}-12-31')
        
        # Download Index of Consumer Expectations
        print("  Fetching Index of Consumer Expectations (UMCSENT1)...")
        try:
            ice = fred.get_series('UMCSENT1',
                                  observation_start=f'{START_YEAR}-01-01',
                                  observation_end=f'{END_YEAR}-12-31')
        except:
            # If not available, use alternative or set to None
            print("    (ICE not available separately, will derive if possible)")
            ice = None
        
        # Download Current Economic Conditions Index
        print("  Fetching Current Economic Conditions (UMCSENT2)...")  
        try:
            icc = fred.get_series('UMCSENT2',
                                  observation_start=f'{START_YEAR}-01-01',
                                  observation_end=f'{END_YEAR}-12-31')
        except:
            print("    (ICC not available separately, will derive if possible)")
            icc = None
        
        # Combine into DataFrame
        df = pd.DataFrame({
            'date': ics.index,
            'ICS_UMICH': ics.values,
        })
        
        if ice is not None and len(ice) > 0:
            df_ice = pd.DataFrame({'date': ice.index, 'ICE_UMICH': ice.values})
            df = df.merge(df_ice, on='date', how='left')
        
        if icc is not None and len(icc) > 0:
            df_icc = pd.DataFrame({'date': icc.index, 'ICC_UMICH': icc.values})
            df = df.merge(df_icc, on='date', how='left')
        
        print(f"  ✓ Successfully downloaded {len(df)} records from FRED")
        print(f"  Columns: {list(df.columns)}")
        
        return df
        
    except ImportError:
        print("fredapi package not installed. Installing now...")
        import subprocess
        subprocess.check_call(['pip', 'install', '-q', 'fredapi'])
        print("  ✓ Installed fredapi. Please run the script again.")
        raise
    except Exception as e:
        print(f"  ✗ Error downloading from FRED: {e}")
        raise

# ==============================================================================
# DATA PROCESSING FUNCTIONS
# ==============================================================================

def process_michigan_data(df):
    """
    Clean and standardize Michigan sentiment data.
    
    Args:
        df: Raw dataframe from Michigan or FRED
        
    Returns:
        pd.DataFrame: Processed sentiment data with standardized columns
    """
    df_clean = df.copy()
    
    # Try to identify date column
    date_cols = [col for col in df_clean.columns if any(x in col.lower() for x in ['date', 'month', 'time', 'period'])]
    
    if date_cols:
        df_clean['date'] = pd.to_datetime(df_clean[date_cols[0]])
    elif df_clean.index.name and 'date' in str(df_clean.index.name).lower():
        df_clean['date'] = pd.to_datetime(df_clean.index)
    else:
        # Try to parse index as date
        try:
            df_clean['date'] = pd.to_datetime(df_clean.index)
        except:
            raise ValueError("Could not identify date column. Please check the data format.")
    
    # Identify sentiment columns
    sentiment_cols = {}
    col_mapping = {
        'ics': ['ics', 'sentiment', 'index', 'umcsent', 'ics_umich'],
        'ice': ['ice', 'expectations', 'expect', 'ice_umich'],
        'icc': ['icc', 'current', 'conditions', 'icc_umich']
    }
    
    for target_name, search_terms in col_mapping.items():
        for col in df_clean.columns:
            if any(term in col.lower() for term in search_terms):
                sentiment_cols[target_name] = col
                break
    
    # Create standardized output
    output_cols = ['date']
    rename_map = {}
    
    if 'ics' in sentiment_cols:
        rename_map[sentiment_cols['ics']] = 'sentiment_michigan_ics'
        output_cols.append('sentiment_michigan_ics')
    
    if 'ice' in sentiment_cols:
        rename_map[sentiment_cols['ice']] = 'sentiment_michigan_ice'
        output_cols.append('sentiment_michigan_ice')
        
    if 'icc' in sentiment_cols:
        rename_map[sentiment_cols['icc']] = 'sentiment_michigan_icc'
        output_cols.append('sentiment_michigan_icc')
    
    df_clean = df_clean.rename(columns=rename_map)
    
    # Select and order columns
    available_cols = [col for col in output_cols if col in df_clean.columns]
    df_clean = df_clean[available_cols]
    
    # Filter date range
    df_clean = df_clean[
        (df_clean['date'].dt.year >= START_YEAR) & 
        (df_clean['date'].dt.year <= END_YEAR)
    ]
    
    # Sort by date
    df_clean = df_clean.sort_values('date').reset_index(drop=True)
    
    # Convert to end-of-month dates for consistency
    df_clean['date'] = pd.to_datetime(df_clean['date']) + pd.offsets.MonthEnd(0)
    
    return df_clean

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("UNIVERSITY OF MICHIGAN CONSUMER SENTIMENT DATA PIPELINE")
    print("="*70)
    print(f"Period: {START_YEAR}-{END_YEAR}")
    print(f"Output: {PROCESSED_DATA_DIR / 'michigan_sentiment.csv'}\n")
    
    # Step 1: Download/Load Data
    print("[Step 1/3] Loading data...")
    
    # Try FRED first (primary method with API key)
    try:
        df_raw = download_from_fred()
    except Exception as fred_error:
        print(f"\nFRED download failed: {fred_error}")
        print("Attempting to load from manual download...")
        try:
            df_raw = download_michigan_data()
        except FileNotFoundError:
            print("\n✗ Could not obtain Michigan sentiment data.")
            print("Please download the data manually or check your FRED API key.")
            return
    
    print(f"✓ Loaded {len(df_raw)} raw records")
    
    # Step 2: Process Data
    print("\n[Step 2/3] Processing and cleaning data...")
    df_processed = process_michigan_data(df_raw)
    print(f"✓ Processed {len(df_processed)} records")
    print(f"  Date range: {df_processed['date'].min()} to {df_processed['date'].max()}")
    print(f"  Columns: {list(df_processed.columns)}")
    
    # Step 3: Save Processed Data
    print("\n[Step 3/3] Saving processed data...")
    output_file = PROCESSED_DATA_DIR / 'michigan_sentiment.csv'
    df_processed.to_csv(output_file, index=False)
    print(f"✓ Saved to: {output_file}")
    
    # Summary statistics
    print("\n" + "="*70)
    print("DATA SUMMARY")
    print("="*70)
    print(df_processed.describe())
    
    print("\n" + "="*70)
    print("✓ Michigan sentiment data processing complete!")
    print("="*70)

if __name__ == "__main__":
    main()
