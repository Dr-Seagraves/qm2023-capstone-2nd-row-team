"""
Fetch and Process Kenneth French Data Library Datasets
======================================================

Downloads factor data from Ken French's Data Library at Dartmouth.
Data period: 2004-2024
Output: data/processed/french_factors.csv

Data includes:
- Fama-French 3 Factors (Market, SMB, HML)
- Momentum Factor (MOM)
- Risk-free rate (RF)
- Market return (Mkt-RF + RF)

Source: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
import io
import zipfile
warnings.filterwarnings('ignore')

from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR

# ==============================================================================
# CONFIGURATION
# ==============================================================================

START_YEAR = 2004
END_YEAR = 2024

# Ken French Data Library URLs
FRENCH_BASE_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"

DATASETS = {
    'ff3': {
        'url': FRENCH_BASE_URL + 'F-F_Research_Data_Factors_CSV.zip',
        'name': 'Fama-French 3 Factors',
        'file': 'F-F_Research_Data_Factors.CSV'
    },
    'mom': {
        'url': FRENCH_BASE_URL + 'F-F_Momentum_Factor_CSV.zip',
        'name': 'Momentum Factor',
        'file': 'F-F_Momentum_Factor.CSV'
    },
    '5factors': {
        'url': FRENCH_BASE_URL + 'F-F_Research_Data_5_Factors_2x3_CSV.zip',
        'name': 'Fama-French 5 Factors',
        'file': 'F-F_Research_Data_5_Factors_2x3.CSV'
    }
}

# ==============================================================================
# DATA DOWNLOAD FUNCTIONS
# ==============================================================================

def download_french_dataset(dataset_key):
    """
    Download a dataset from Ken French Data Library.
    
    Args:
        dataset_key: Key from DATASETS dict ('ff3', 'mom', etc.)
        
    Returns:
        pd.DataFrame: Monthly factor returns
    """
    try:
        import requests
        
        dataset_info = DATASETS[dataset_key]
        url = dataset_info['url']
        name = dataset_info['name']
        
        print(f"  Downloading {name}...")
        print(f"  URL: {url}")
        
        # Download the ZIP file
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Extract CSV from ZIP
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            # Get the CSV file name from the ZIP
            csv_files = [f for f in zip_file.namelist() if f.endswith('.CSV') or f.endswith('.csv')]
            
            if not csv_files:
                raise ValueError(f"No CSV file found in {url}")
            
            csv_file = csv_files[0]
            
            # Read the CSV content
            with zip_file.open(csv_file) as f:
                content = f.read().decode('utf-8', errors='ignore')
        
        # Save raw content for reference
        raw_file = RAW_DATA_DIR / f'french_{dataset_key}.csv'
        with open(raw_file, 'w') as f:
            f.write(content)
        print(f"  ✓ Saved raw data to: {raw_file}")
        
        # Parse the CSV (French data has specific format)
        df = parse_french_csv(content, dataset_key)
        
        return df
        
    except ImportError:
        print("requests package not installed. Run: pip install requests")
        raise
    except Exception as e:
        print(f"  ✗ Error downloading {name}: {e}")
        raise

def parse_french_csv(content, dataset_key):
    """
    Parse Ken French CSV format.
    
    French CSVs have a specific format:
    - Header rows with descriptions
    - Monthly data section
    - Annual data section (which we skip)
    
    Args:
        content: CSV file content as string
        dataset_key: Type of dataset
        
    Returns:
        pd.DataFrame: Parsed monthly data
    """
    lines = content.strip().split('\n')
    
    # Find the start of monthly data (usually after blank lines and headers)
    data_start = 0
    for i, line in enumerate(lines):
        # Look for the column header line (contains "Mkt-RF" or similar)
        if 'Mkt-RF' in line or 'Mom' in line or 'SMB' in line:
            data_start = i
            break
    
    if data_start == 0:
        # Fallback: assume data starts after first few lines
        data_start = min(3, len(lines))
    
    # Find the end of monthly data (before annual data)
    data_end = len(lines)
    for i, line in enumerate(lines[data_start + 1:], start=data_start + 1):
        # Annual data typically starts with a year like "1927" or blank line
        if line.strip() == '' or (line.strip().isdigit() and len(line.strip()) == 4):
            data_end = i
            break
    
    # Extract monthly data section
    monthly_section = '\n'.join(lines[data_start:data_end])
    
    # Read into DataFrame
    df = pd.read_csv(io.StringIO(monthly_section), skipinitialspace=True)
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Parse date column (usually first column, format YYYYMM)
    date_col = df.columns[0]
    
    # Convert YYYYMM to datetime
    if df[date_col].dtype == 'object':
        df[date_col] = df[date_col].astype(str).str.strip()
    
    df['date'] = pd.to_datetime(df[date_col].astype(str), format='%Y%m', errors='coerce')
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['date'])
    
    # Drop original date column
    df = df.drop(columns=[date_col])
    
    # Convert factor returns to numeric
    for col in df.columns:
        if col != 'date':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

# ==============================================================================
# DATA PROCESSING FUNCTIONS
# ==============================================================================

def process_french_data(df_ff3, df_mom=None, df_5f=None):
    """
    Combine and standardize French factor data.
    
    Args:
        df_ff3: Fama-French 3 factors
        df_mom: Momentum factor (optional)
        df_5f: Fama-French 5 factors (optional)
        
    Returns:
        pd.DataFrame: Combined factor dataset
    """
    # Start with 3-factor model
    df = df_ff3.copy()
    
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Standardize column names
    rename_map = {
        'Mkt-RF': 'mkt_rf',
        'SMB': 'smb',
        'HML': 'hml',
        'RF': 'rf'
    }
    
    df = df.rename(columns=rename_map)
    
    # Calculate total market return
    if 'mkt_rf' in df.columns and 'rf' in df.columns:
        df['mkt_ret'] = df['mkt_rf'] + df['rf']
    
    # Merge momentum if available
    if df_mom is not None and len(df_mom) > 0:
        df_mom = df_mom.copy()
        df_mom['date'] = pd.to_datetime(df_mom['date'])
        
        # Rename momentum column
        mom_cols = [c for c in df_mom.columns if c != 'date']
        if mom_cols:
            mom_col = mom_cols[0]
            df_mom = df_mom.rename(columns={mom_col: 'mom'})
            df = df.merge(df_mom[['date', 'mom']], on='date', how='left')
    
    # Merge 5-factor data if available
    if df_5f is not None and len(df_5f) > 0:
        df_5f = df_5f.copy()
        df_5f['date'] = pd.to_datetime(df_5f['date'])
        
        # Extract RMW and CMA factors
        factor_cols = {}
        for col in df_5f.columns:
            if 'RMW' in col:
                factor_cols['rmw'] = col
            elif 'CMA' in col:
                factor_cols['cma'] = col
        
        if factor_cols:
            rename_5f = {v: k for k, v in factor_cols.items()}
            df_5f = df_5f.rename(columns=rename_5f)
            merge_cols = ['date'] + list(factor_cols.keys())
            df = df.merge(df_5f[merge_cols], on='date', how='left')
    
    # Filter date range
    df = df[
        (df['date'].dt.year >= START_YEAR) & 
        (df['date'].dt.year <= END_YEAR)
    ]
    
    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)
    
    # Convert to end-of-month dates
    df['date'] = pd.to_datetime(df['date']) + pd.offsets.MonthEnd(0)
    
    return df

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("KENNETH FRENCH DATA LIBRARY PIPELINE")
    print("="*70)
    print(f"Period: {START_YEAR}-{END_YEAR}")
    print(f"Output: {PROCESSED_DATA_DIR / 'french_factors.csv'}\n")
    
    # Step 1: Download Data
    print("[Step 1/3] Downloading French factor data...")
    
    try:
        # Download 3-factor model (required)
        df_ff3 = download_french_dataset('ff3')
        print(f"  ✓ Fama-French 3 Factors: {len(df_ff3)} records")
        
        # Download momentum (optional)
        try:
            df_mom = download_french_dataset('mom')
            print(f"  ✓ Momentum Factor: {len(df_mom)} records")
        except Exception as e:
            print(f"  ⚠ Could not download momentum: {e}")
            df_mom = None
        
        # Download 5-factor model (optional, for additional factors)
        try:
            df_5f = download_french_dataset('5factors')
            print(f"  ✓ Fama-French 5 Factors: {len(df_5f)} records")
        except Exception as e:
            print(f"  ⚠ Could not download 5-factors: {e}")
            df_5f = None
            
    except Exception as e:
        print(f"\n✗ Error downloading data: {e}")
        print("\nPlease check your internet connection and try again.")
        return
    
    # Step 2: Process Data
    print("\n[Step 2/3] Processing and merging factor data...")
    df_processed = process_french_data(df_ff3, df_mom, df_5f)
    print(f"✓ Processed {len(df_processed)} records")
    print(f"  Date range: {df_processed['date'].min()} to {df_processed['date'].max()}")
    print(f"  Factors included: {[c for c in df_processed.columns if c != 'date']}")
    
    # Step 3: Save Processed Data
    print("\n[Step 3/3] Saving processed data...")
    output_file = PROCESSED_DATA_DIR / 'french_factors.csv'
    df_processed.to_csv(output_file, index=False)
    print(f"✓ Saved to: {output_file}")
    
    # Summary statistics
    print("\n" + "="*70)
    print("DATA SUMMARY")
    print("="*70)
    print(df_processed.describe())
    
    print("\n" + "="*70)
    print("✓ French factor data processing complete!")
    print("="*70)

if __name__ == "__main__":
    main()
