"""
Automated Download of University of Michigan Consumer Sentiment Data
====================================================================

Downloads Michigan Survey of Consumers data from FRED (Federal Reserve Economic Data).
Data period: 2004-2024

FRED hosts the official University of Michigan data publicly:
- UMCSENT: Index of Consumer Sentiment
- UMCSENT: Consumer Sentiment (same series, main index)

Source: Federal Reserve Bank of St. Louis (FRED)
Website: https://fred.stlouisfed.org/
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

# FRED Series IDs for Michigan data
FRED_SERIES = {
    'UMCSENT': 'Index of Consumer Sentiment',
    'UMCSENT_FUTURE': 'Index of Consumer Expectations (ICE)', 
    'UMCSENT_CURRENT': 'Current Economic Conditions (ICC)'
}

# Note: FRED only has UMCSENT as the main series
# The subindices may need to be obtained separately or from the official Michigan source

# ==============================================================================
# DOWNLOAD FUNCTIONS
# ==============================================================================

def download_from_fred():
    """
    Download Michigan sentiment data from FRED using pandas_datareader.
    
    Returns:
        pd.DataFrame: Michigan sentiment data
    """
    try:
        import pandas_datareader.data as web
        
        print("Downloading Michigan Consumer Sentiment from FRED...")
        print(f"Period: {START_YEAR}-01-01 to {END_YEAR}-12-31")
        
        start_date = f'{START_YEAR}-01-01'
        end_date = f'{END_YEAR}-12-31'
        
        # Download Index of Consumer Sentiment (main series)
        print("\n  Fetching UMCSENT (Index of Consumer Sentiment)...")
        ics = web.DataReader('UMCSENT', 'fred', start_date, end_date)
        print(f"  ✓ Downloaded {len(ics)} records")
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': ics.index,
            'ICS_UMICH': ics['UMCSENT'].values
        })
        
        # Try to get consumer expectations if available
        try:
            print("\n  Attempting to fetch Index of Consumer Expectations...")
            # Note: FRED may not have separate ICE/ICC series
            # The official Michigan source separates these, but FRED primarily has UMCSENT
            pass
        except:
            print("  Note: Consumer Expectations not available separately on FRED")
        
        df = df.reset_index(drop=True)
        
        print(f"\n✓ Successfully downloaded {len(df)} monthly records")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        
        return df
        
    except ImportError:
        print("\n✗ Error: pandas_datareader not installed")
        print("\nInstall with:")
        print("  pip install pandas-datareader")
        raise
    except Exception as e:
        print(f"\n✗ Error downloading from FRED: {e}")
        raise

def download_from_fred_csv():
    """
    Alternative: Download directly from FRED CSV download URL.
    This doesn't require pandas_datareader.
    
    Returns:
        pd.DataFrame: Michigan sentiment data
    """
    try:
        import requests
        from io import StringIO
        
        print("Downloading Michigan Consumer Sentiment from FRED (CSV)...")
        
        # FRED provides direct CSV download URLs
        url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=UMCSENT'
        
        # Add date parameters
        params = {
            'cosd': f'{START_YEAR}-01-01',
            'coed': f'{END_YEAR}-12-31'
        }
        
        print(f"  URL: {url}")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        # Parse CSV
        df = pd.read_csv(StringIO(response.text))
        
        # Rename columns
        df.columns = ['date', 'ICS_UMICH']
        df['date'] = pd.to_datetime(df['date'])
        
        # Handle missing values (FRED uses '.' for missing)
        df['ICS_UMICH'] = pd.to_numeric(df['ICS_UMICH'], errors='coerce')
        
        # Filter date range
        df = df[
            (df['date'].dt.year >= START_YEAR) & 
            (df['date'].dt.year <= END_YEAR)
        ]
        
        print(f"\n✓ Successfully downloaded {len(df)} records")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        
        return df
        
    except ImportError:
        print("requests package not installed. Run: pip install requests")
        raise
    except Exception as e:
        print(f"Error downloading from FRED CSV: {e}")
        raise

# ==============================================================================
# DATA PROCESSING
# ==============================================================================

def process_michigan_data(df):
    """
    Process and clean Michigan sentiment data.
    
    Args:
        df: Raw Michigan data
        
    Returns:
        pd.DataFrame: Processed data
    """
    df_clean = df.copy()
    
    # Ensure date is datetime
    df_clean['date'] = pd.to_datetime(df_clean['date'])
    
    # Convert to end-of-month dates for consistency
    df_clean['date'] = df_clean['date'] + pd.offsets.MonthEnd(0)
    
    # Remove any duplicates
    df_clean = df_clean.drop_duplicates(subset=['date'], keep='last')
    
    # Sort by date
    df_clean = df_clean.sort_values('date').reset_index(drop=True)
    
    # Rename for consistency
    df_clean = df_clean.rename(columns={'ICS_UMICH': 'sentiment_michigan_ics'})
    
    return df_clean

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("MICHIGAN CONSUMER SENTIMENT - AUTOMATED DOWNLOAD")
    print("="*70)
    print(f"Period: {START_YEAR}-{END_YEAR}")
    print("Source: Federal Reserve Economic Data (FRED)")
    print(f"Output: {PROCESSED_DATA_DIR / 'michigan_sentiment.csv'}\n")
    
    # Step 1: Download Data
    print("[Step 1/3] Downloading data from FRED...")
    
    try:
        # Try pandas_datareader first (more reliable)
        df_raw = download_from_fred()
    except ImportError:
        print("\nFalling back to direct CSV download...")
        try:
            df_raw = download_from_fred_csv()
        except Exception as e:
            print(f"\n✗ Download failed: {e}")
            print("\nAlternative: Install pandas_datareader and try again:")
            print("  pip install pandas-datareader")
            return
    except Exception as e:
        print(f"\nError with pandas_datareader, trying CSV download...")
        try:
            df_raw = download_from_fred_csv()
        except Exception as e2:
            print(f"\n✗ All download methods failed")
            print(f"  pandas_datareader error: {e}")
            print(f"  CSV download error: {e2}")
            return
    
    # Save raw data
    raw_file = RAW_DATA_DIR / 'michigan_consumer_sentiment.csv'
    df_raw.to_csv(raw_file, index=False)
    print(f"\n✓ Saved raw data to: {raw_file}")
    
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
    
    # Check for missing values
    missing = df_processed['sentiment_michigan_ics'].isna().sum()
    if missing > 0:
        print(f"\n⚠ Warning: {missing} missing values found")
    else:
        print("\n✓ No missing values")
    
    # Display sample data
    print("\n" + "="*70)
    print("SAMPLE DATA (First 5 and Last 5 rows)")
    print("="*70)
    print("\nFirst 5 rows:")
    print(df_processed.head())
    print("\nLast 5 rows:")
    print(df_processed.tail())
    
    print("\n" + "="*70)
    print("✓ Michigan sentiment data download complete!")
    print("="*70)
    print("\nData saved to:")
    print(f"  Raw: {raw_file}")
    print(f"  Processed: {output_file}")
    print("\nNote: FRED provides the main Index of Consumer Sentiment (ICS).")
    print("If you need the subindices (ICE, ICC), you may need to access")
    print("the official Michigan source via: https://data.sca.isr.umich.edu/")

if __name__ == "__main__":
    main()
