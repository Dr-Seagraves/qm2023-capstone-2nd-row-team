"""
Process AAII Sentiment Data from Excel File
===========================================
Processes the AAII sentiment.xls file that was uploaded.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR

def main():
    print("\n" + "="*70)
    print("AAII SENTIMENT DATA - PROCESSING UPLOADED FILE")
    print("="*70)
    
    # Read the Excel file
    print("\n[Step 1/3] Loading Excel file...")
    df_raw = pd.read_excel(RAW_DATA_DIR / 'aaii_sentiment.xls', skiprows=6, header=None)
    
    # Assign column names based on file structure
    df_raw.columns = [
        'Reported_Date', 'Bullish', 'Neutral', 'Bearish', 'Total',
        '8week_MovAvg', 'BullBear_Spread', 'Bullish_Avg', 
        'Bullish_Plus_StDev', 'Bullish_Minus_StDev',
        'SP500_High', 'SP500_Low', 'SP500_Close', 'Extra'
    ]
    
    # Remove summary rows
    df_clean = df_raw[~df_raw['Reported_Date'].astype(str).str.contains('Count', na=False)].copy()
    
    # Convert date
    df_clean['Reported_Date'] = pd.to_datetime(df_clean['Reported_Date'], errors='coerce')
    df_clean = df_clean.dropna(subset=['Reported_Date'])
    
    # Convert sentiment columns to numeric and multiply by 100 (convert from decimal to percentage)
    for col in ['Bullish', 'Neutral', 'Bearish']:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce') * 100
    
    print(f"✓ Loaded {len(df_clean)} total records")
    print(f"  Date range: {df_clean['Reported_Date'].min()} to {df_clean['Reported_Date'].max()}")
    
    # Filter to 2004-2024
    print("\n[Step 2/3] Filtering to 2004-2024...")
    df_filtered = df_clean[
        (df_clean['Reported_Date'].dt.year >= 2004) & 
        (df_clean['Reported_Date'].dt.year <= 2024)
    ].copy()
    
    print(f"✓ Filtered to {len(df_filtered)} records")
    
    # Create final output
    df_output = df_filtered[['Reported_Date', 'Bullish', 'Neutral', 'Bearish']].copy()
    df_output = df_output.rename(columns={
        'Reported_Date': 'date',
        'Bullish': 'bullish_pct',
        'Neutral': 'neutral_pct',
        'Bearish': 'bearish_pct'
    })
    
    # Calculate bull-bear spread
    df_output['bull_bear_spread'] = df_output['bullish_pct'] - df_output['bearish_pct']
    
    # Sort by date
    df_output = df_output.sort_values('date').reset_index(drop=True)
    
    # Remove any duplicates
    df_output = df_output.drop_duplicates(subset=['date'], keep='last')
    
    print(f"✓ Created {len(df_output)} processed records")
    print(f"  Columns: {list(df_output.columns)}")
    
    # Save processed data
    print("\n[Step 3/3] Saving processed data...")
    output_file = PROCESSED_DATA_DIR / 'aaii_sentiment.csv'
    df_output.to_csv(output_file, index=False)
    print(f"✓ Saved to: {output_file}")
    
    # Summary statistics
    print("\n" + "="*70)
    print("DATA SUMMARY")
    print("="*70)
    print(df_output.describe())
    
    # Sample data
    print("\n" + "="*70)
    print("SAMPLE DATA")
    print("="*70)
    print("\nFirst 5 rows:")
    print(df_output.head())
    print("\nLast 5 rows:")
    print(df_output.tail())
    
    print("\n" + "="*70)
    print("✓ AAII SENTIMENT DATA PROCESSING COMPLETE!")
    print("="*70)
    print(f"\nProcessed {len(df_output)} weekly observations")
    print(f"Period: {df_output['date'].min().strftime('%Y-%m-%d')} to {df_output['date'].max().strftime('%Y-%m-%d')}")
    print(f"Output: {output_file}")

if __name__ == "__main__":
    main()
