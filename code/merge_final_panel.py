"""
Merge Final Panel Dataset
=========================

Combines all processed datasets into a final panel for analysis.

Inputs (from data/processed/):
- michigan_sentiment.csv - University of Michigan Consumer Sentiment
- aaii_sentiment.csv - AAII Investor Sentiment Survey  
- french_factors.csv - Kenneth French Factor Data

Output: data/final/analysis_panel.csv

Merging strategy:
- Primary frequency: Monthly
- AAII weekly data is aggregated to monthly
- All datasets merged on end-of-month dates
- Missing values handled appropriately
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from config_paths import PROCESSED_DATA_DIR, FINAL_DATA_DIR

# ==============================================================================
# CONFIGURATION
# ==============================================================================

START_YEAR = 2004
END_YEAR = 2024

# Input files
INPUT_FILES = {
    'michigan': PROCESSED_DATA_DIR / 'michigan_sentiment.csv',
    'aaii': PROCESSED_DATA_DIR / 'aaii_sentiment.csv',
    'french': PROCESSED_DATA_DIR / 'french_factors.csv',
}

# Output file
OUTPUT_FILE = FINAL_DATA_DIR / 'analysis_panel.csv'

# ==============================================================================
# DATA LOADING FUNCTIONS
# ==============================================================================

def load_processed_data():
    """
    Load all processed datasets.
    
    Returns:
        dict: Dictionary of DataFrames with keys from INPUT_FILES
    """
    datasets = {}
    
    for name, filepath in INPUT_FILES.items():
        if filepath.exists():
            print(f"  Loading {name}...")
            df = pd.read_csv(filepath)
            df['date'] = pd.to_datetime(df['date'])
            datasets[name] = df
            print(f"    ✓ {len(df)} records, {len(df.columns)} columns")
        else:
            print(f"  ⚠ Warning: {name} not found at {filepath}")
            datasets[name] = None
    
    return datasets

# ==============================================================================
# DATA AGGREGATION FUNCTIONS
# ==============================================================================

def aggregate_aaii_to_monthly(df_aaii):
    """
    Aggregate AAII weekly data to monthly frequency.
    
    Strategy:
    - Use last week of each month as the monthly value
    - Alternative: could use average of all weeks in month
    
    Args:
        df_aaii: Weekly AAII sentiment data
        
    Returns:
        pd.DataFrame: Monthly AAII data
    """
    if df_aaii is None or len(df_aaii) == 0:
        return None
    
    df = df_aaii.copy()
    
    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Convert to end-of-month dates
    df['month_end'] = df['date'] + pd.offsets.MonthEnd(0)
    
    # Drop the original date column to avoid duplication
    df = df.drop('date', axis=1)
    
    # Group by month and take last observation (most recent in that month)
    # Alternative: use .mean() to average all weeks in a month
    monthly_data = df.groupby('month_end').last().reset_index()
    
    # Rename month_end to date
    monthly_data = monthly_data.rename(columns={'month_end': 'date'})
    
    return monthly_data

# ==============================================================================
# DATA MERGING FUNCTIONS
# ==============================================================================

def create_date_index(start_year, end_year):
    """
    Create a complete monthly date index.
    
    Args:
        start_year: Start year
        end_year: End year
        
    Returns:
        pd.DataFrame: DataFrame with complete monthly dates
    """
    start_date = f'{start_year}-01-01'
    end_date = f'{end_year}-12-31'
    
    # Use 'ME' for month end (newer pandas) or 'M' for older versions
    try:
        date_range = pd.date_range(start=start_date, end=end_date, freq='ME')
    except:
        date_range = pd.date_range(start=start_date, end=end_date, freq='M')
    
    df_dates = pd.DataFrame({'date': date_range})
    
    return df_dates

def merge_datasets(datasets):
    """
    Merge all datasets into a single panel.
    
    Args:
        datasets: Dictionary of processed DataFrames
        
    Returns:
        pd.DataFrame: Merged panel dataset
    """
    # Create complete date index
    df_panel = create_date_index(START_YEAR, END_YEAR)
    print(f"\n  Created date index: {len(df_panel)} months")
    
    # Merge Michigan sentiment
    if datasets['michigan'] is not None:
        df_panel = df_panel.merge(
            datasets['michigan'],
            on='date',
            how='left'
        )
        print(f"  ✓ Merged Michigan sentiment")
    
    # Aggregate and merge AAII sentiment
    if datasets['aaii'] is not None:
        df_aaii_monthly = aggregate_aaii_to_monthly(datasets['aaii'])
        if df_aaii_monthly is not None:
            df_panel = df_panel.merge(
                df_aaii_monthly,
                on='date',
                how='left'
            )
            print(f"  ✓ Merged AAII sentiment (aggregated to monthly)")
    
    # Merge French factors
    if datasets['french'] is not None:
        df_panel = df_panel.merge(
            datasets['french'],
            on='date',
            how='left'
        )
        print(f"  ✓ Merged French factors")
    
    return df_panel

# ==============================================================================
# DATA QUALITY FUNCTIONS
# ==============================================================================

def check_data_quality(df):
    """
    Perform data quality checks and report missing values.
    
    Args:
        df: Merged panel DataFrame
    """
    print("\n" + "="*70)
    print("DATA QUALITY REPORT")
    print("="*70)
    
    # Time coverage
    print(f"\nTime Coverage:")
    print(f"  Start date: {df['date'].min()}")
    print(f"  End date: {df['date'].max()}")
    print(f"  Total months: {len(df)}")
    
    # Missing values
    print(f"\nMissing Values:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    
    missing_df = pd.DataFrame({
        'Column': missing.index,
        'Missing': missing.values,
        'Percent': missing_pct.values
    })
    missing_df = missing_df[missing_df['Missing'] > 0].sort_values('Missing', ascending=False)
    
    if len(missing_df) > 0:
        print(missing_df.to_string(index=False))
    else:
        print("  ✓ No missing values!")
    
    # Data availability by year
    print(f"\nData Availability by Year:")
    df['year'] = df['date'].dt.year
    
    # Count non-null values per year for key variables
    key_vars = [col for col in df.columns if col not in ['date', 'year']]
    
    for var in key_vars[:5]:  # Show first 5 variables
        available = df.groupby('year')[var].count()
        print(f"  {var}: {available.min()}-{available.max()} months/year")
    
    df.drop('year', axis=1, inplace=True)

def create_summary_statistics(df):
    """
    Generate summary statistics for the panel.
    
    Args:
        df: Merged panel DataFrame
        
    Returns:
        pd.DataFrame: Summary statistics
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    summary = df[numeric_cols].describe()
    
    return summary

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("MERGE FINAL PANEL DATASET")
    print("="*70)
    print(f"Period: {START_YEAR}-{END_YEAR}")
    print(f"Output: {OUTPUT_FILE}\n")
    
    # Step 1: Load processed datasets
    print("[Step 1/4] Loading processed datasets...")
    datasets = load_processed_data()
    
    # Check if we have any data
    if all(v is None for v in datasets.values()):
        print("\n✗ Error: No processed datasets found!")
        print("Please run the fetch scripts first:")
        print("  - python code/fetch_michigan_sentiment.py")
        print("  - python code/fetch_aaii_sentiment.py")
        print("  - python code/fetch_french_factors.py")
        return
    
    # Step 2: Merge datasets
    print("\n[Step 2/4] Merging datasets...")
    df_panel = merge_datasets(datasets)
    print(f"  ✓ Final panel: {len(df_panel)} rows × {len(df_panel.columns)} columns")
    
    # Step 3: Data quality checks
    print("\n[Step 3/4] Checking data quality...")
    check_data_quality(df_panel)
    
    # Step 4: Save final dataset
    print("\n[Step 4/4] Saving final panel...")
    df_panel.to_csv(OUTPUT_FILE, index=False)
    print(f"✓ Saved to: {OUTPUT_FILE}")
    
    # Generate summary statistics
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    summary = create_summary_statistics(df_panel)
    print(summary)
    
    # Save summary statistics
    summary_file = FINAL_DATA_DIR / 'summary_statistics.csv'
    summary.to_csv(summary_file)
    print(f"\n✓ Summary statistics saved to: {summary_file}")
    
    print("\n" + "="*70)
    print("✓ Panel dataset creation complete!")
    print("="*70)
    print(f"\nFinal dataset ready for analysis:")
    print(f"  Location: {OUTPUT_FILE}")
    print(f"  Dimensions: {len(df_panel)} rows × {len(df_panel.columns)} columns")
    print(f"  Variables: {list(df_panel.columns)}")
    print("\nNext steps:")
    print("  1. Load the panel: df = pd.read_csv('data/final/analysis_panel.csv')")
    print("  2. Begin your analysis!")

if __name__ == "__main__":
    main()
