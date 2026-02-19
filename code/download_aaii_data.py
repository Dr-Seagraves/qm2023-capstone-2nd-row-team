"""
Fetch and Process AAII Investor Sentiment Survey Data
=====================================================

Downloads investor sentiment data from AAII Sentiment Survey.
Data period: 2004-2024
Output: data/processed/aaii_sentiment.csv

Source: https://www.aaii.com/sentimentsurvey/sent_results
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
import time
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

def download_aaii_data_web():
    """
    Download AAII sentiment data from the web page.
    Uses requests with proper headers to access the data.
    
    Returns:
        pd.DataFrame: AAII sentiment data
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        print(f"Downloading AAII sentiment data from: {AAII_URL}")
        
        # Set up headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        # Make request with timeout
        session = requests.Session()
        response = session.get(AAII_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # The data is typically in a table - try to find it
        # AAII page structure may have the data in a table with class or id
        tables = pd.read_html(response.text)
        
        if not tables:
            print("  ✗ No tables found on the page")
            return None
        
        # The first table usually contains the sentiment data
        df = tables[0]
        
        print(f"  ✓ Found table with {len(df)} rows and {len(df.columns)} columns")
        print(f"  Columns: {list(df.columns)}")
        
        # Save raw HTML for debugging
        raw_html_file = RAW_DATA_DIR / 'aaii_sentiment_page.html'
        with open(raw_html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"  ✓ Saved raw HTML to: {raw_html_file}")
        
        return df
        
    except ImportError as e:
        print(f"  ✗ Required package not installed: {e}")
        print("  Install with: pip install requests beautifulsoup4 lxml")
        raise
    except Exception as e:
        print(f"  ✗ Error downloading from AAII website: {e}")
        raise

def download_aaii_data_csv():
    """
    Alternative: Try to download AAII data as CSV if available.
    Some pages offer a direct CSV download link.
    
    Returns:
        pd.DataFrame: AAII sentiment data
    """
    try:
        import requests
        
        # Check if there's a direct CSV download link
        # Note: This URL may need to be updated based on actual AAII site structure
        csv_url = "https://www.aaii.com/files/surveys/sentiment.xls"
        
        print(f"  Attempting direct CSV/Excel download...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(csv_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Try to parse as Excel
            from io import BytesIO
            df = pd.read_excel(BytesIO(response.content))
            print(f"  ✓ Downloaded Excel file with {len(df)} records")
            return df
        else:
            print(f"  Direct download not available (status {response.status_code})")
            return None
            
    except Exception as e:
        print(f"  Direct download failed: {e}")
        return None

def load_manual_file():
    """
    Load AAII data from manually downloaded file.
    
    Returns:
        pd.DataFrame: AAII sentiment data
    """
    # Check for various file formats
    possible_files = [
        RAW_DATA_DIR / 'aaii_sentiment.csv',
        RAW_DATA_DIR / 'aaii_sentiment.xlsx',
        RAW_DATA_DIR / 'aaii_sentiment.xls',
        RAW_DATA_DIR / 'sent_results.csv',
        RAW_DATA_DIR / 'sent_results.xlsx',
    ]
    
    for filepath in possible_files:
        if filepath.exists():
            print(f"  ✓ Found manual download: {filepath}")
            
            if filepath.suffix == '.csv':
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
            
            print(f"  ✓ Loaded {len(df)} records")
            return df
    
    return None

# ==============================================================================
# DATA PROCESSING FUNCTIONS
# ==============================================================================

def process_aaii_data(df):
    """
    Clean and standardize AAII sentiment data.
    
    Expected columns (will auto-detect):
    - Date/Week Ending/Reported Date
    - Bullish % 
    - Neutral %
    - Bearish %
    
    Args:
        df: Raw AAII dataframe
        
    Returns:
        pd.DataFrame: Processed sentiment data
    """
    df_clean = df.copy()
    
    print("\n  Processing AAII data...")
    print(f"  Original columns: {list(df_clean.columns)}")
    
    # Detect and standardize date column
    date_cols = [col for col in df_clean.columns 
                 if any(x in str(col).lower() for x in ['date', 'week', 'time', 'period', 'reported'])]
    
    if date_cols:
        date_col = date_cols[0]
        print(f"  Using date column: {date_col}")
        df_clean['date'] = pd.to_datetime(df_clean[date_col], errors='coerce')
    else:
        # Try to parse index
        try:
            df_clean['date'] = pd.to_datetime(df_clean.index)
        except:
            print("  ✗ Could not identify date column")
            print(f"  Available columns: {list(df_clean.columns)}")
            raise ValueError("Could not identify date column")
    
    # Remove rows with invalid dates
    df_clean = df_clean.dropna(subset=['date'])
    
    # Detect sentiment columns - look for percentage columns
    column_mapping = {}
    
    # Look for bullish percentage
    for col in df_clean.columns:
        col_lower = str(col).lower()
        if 'bull' in col_lower and '%' not in str(col):  # Column name, not value
            column_mapping[col] = 'bullish_pct'
            break
        elif col_lower == 'bullish':
            column_mapping[col] = 'bullish_pct'
            break
    
    # Look for bearish percentage
    for col in df_clean.columns:
        col_lower = str(col).lower()
        if 'bear' in col_lower and 'bull' not in col_lower and '%' not in str(col):
            column_mapping[col] = 'bearish_pct'
            break
        elif col_lower == 'bearish':
            column_mapping[col] = 'bearish_pct'
            break
    
    # Look for neutral percentage
    for col in df_clean.columns:
        col_lower = str(col).lower()
        if 'neutral' in col_lower and '%' not in str(col):
            column_mapping[col] = 'neutral_pct'
            break
        elif col_lower == 'neutral':
            column_mapping[col] = 'neutral_pct'
            break
    
    print(f"  Column mapping: {column_mapping}")
    
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
            # Handle different formats
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].astype(str).str.replace('%', '').str.replace(',', '')
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
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
    
    # Remove duplicates (keep most recent)
    df_clean = df_clean.drop_duplicates(subset=['date'], keep='last')
    
    print(f"  ✓ Processed {len(df_clean)} records")
    print(f"  Date range: {df_clean['date'].min()} to {df_clean['date'].max()}")
    
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
    print("[Step 1/3] Loading AAII data...")
    
    df_raw = None
    
    # Try method 1: Manual file first
    print("\nAttempting to load from manual download...")
    df_raw = load_manual_file()
    
    # Try method 2: Web scraping
    if df_raw is None:
        print("\nAttempting to download from AAII website...")
        try:
            df_raw = download_aaii_data_web()
        except Exception as e:
            print(f"Web download failed: {e}")
    
    # Try method 3: Direct CSV/Excel download
    if df_raw is None:
        print("\nAttempting direct file download...")
        try:
            df_raw = download_aaii_data_csv()
        except Exception as e:
            print(f"Direct download failed: {e}")
    
    # If all methods failed
    if df_raw is None or len(df_raw) == 0:
        print("\n" + "="*70)
        print("MANUAL DOWNLOAD REQUIRED")
        print("="*70)
        print("\nCould not automatically download AAII data.")
        print("\nPlease follow these steps:")
        print("\n1. Visit: https://www.aaii.com/sentimentsurvey/sent_results")
        print("2. If you have AAII membership, log in")
        print("3. Download or copy the sentiment data table")
        print("4. Save as one of these files:")
        print(f"   - {RAW_DATA_DIR / 'aaii_sentiment.csv'}")
        print(f"   - {RAW_DATA_DIR / 'aaii_sentiment.xlsx'}")
        print("\nThen run this script again.")
        print("="*70)
        return
    
    print(f"\n✓ Loaded {len(df_raw)} raw records")
    print(f"  Columns: {list(df_raw.columns)}")
    
    # Save raw data
    raw_file = RAW_DATA_DIR / 'aaii_sentiment_raw.csv'
    df_raw.to_csv(raw_file, index=False)
    print(f"  ✓ Saved raw data to: {raw_file}")
    
    # Step 2: Process Data
    print("\n[Step 2/3] Processing and cleaning data...")
    try:
        df_processed = process_aaii_data(df_raw)
    except Exception as e:
        print(f"\n✗ Error processing data: {e}")
        print("\nRaw data preview:")
        print(df_raw.head())
        return
    
    # Check data quality
    if len(df_processed) < 52:  # Less than one year of weekly data
        print(f"\n⚠ Warning: Only {len(df_processed)} records found.")
        print("  Expected ~1000+ weekly records for 2004-2024.")
        print("  You may need to download more historical data.")
    
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
    
    # Sample data
    print("\n" + "="*70)
    print("SAMPLE DATA")
    print("="*70)
    print("\nFirst 5 rows:")
    print(df_processed.head())
    print("\nLast 5 rows:")
    print(df_processed.tail())
    
    print("\n" + "="*70)
    print("✓ AAII sentiment data processing complete!")
    print("="*70)

if __name__ == "__main__":
    main()
