"""
Master Script - Run All Data Fetch and Merge Scripts
====================================================

Executes the complete data pipeline in sequence:
1. Fetch Michigan Consumer Sentiment
2. Fetch AAII Sentiment Survey
3. Fetch Ken French Factors
4. Merge into final panel dataset

Usage:
    python code/run_all_fetch_scripts.py
    
    Or run individually:
    python code/fetch_michigan_sentiment.py
    python code/fetch_aaii_sentiment.py
    python code/fetch_french_factors.py
    python code/merge_final_panel.py
"""

import sys
from pathlib import Path

# Add code directory to path
CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

# ==============================================================================
# IMPORT FETCH SCRIPTS
# ==============================================================================

print("\n" + "="*70)
print("CAPSTONE DATA PIPELINE - MASTER SCRIPT")
print("="*70)
print("\nThis script will:")
print("  1. Download/process Michigan Consumer Sentiment data")
print("  2. Download/process AAII Investor Sentiment data")
print("  3. Download/process Ken French Factor data")
print("  4. Merge all datasets into final analysis panel")
print("\n" + "="*70)

# ==============================================================================
# STEP 1: MICHIGAN SENTIMENT
# ==============================================================================

print("\n\n")
print("#" * 70)
print("# STEP 1/4: MICHIGAN CONSUMER SENTIMENT")
print("#" * 70)

try:
    import fetch_michigan_sentiment
    fetch_michigan_sentiment.main()
    michigan_success = True
except Exception as e:
    print(f"\n⚠ Warning: Michigan sentiment fetch failed: {e}")
    print("You may need to download this data manually.")
    michigan_success = False

# ==============================================================================
# STEP 2: AAII SENTIMENT
# ==============================================================================

print("\n\n")
print("#" * 70)
print("# STEP 2/4: AAII INVESTOR SENTIMENT")
print("#" * 70)

try:
    import fetch_aaii_sentiment
    fetch_aaii_sentiment.main()
    aaii_success = True
except Exception as e:
    print(f"\n⚠ Warning: AAII sentiment fetch failed: {e}")
    print("You may need to download this data manually.")
    aaii_success = False

# ==============================================================================
# STEP 3: FRENCH FACTORS
# ==============================================================================

print("\n\n")
print("#" * 70)
print("# STEP 3/4: KEN FRENCH FACTOR DATA")
print("#" * 70)

try:
    import fetch_french_factors
    fetch_french_factors.main()
    french_success = True
except Exception as e:
    print(f"\n✗ Error: French factors fetch failed: {e}")
    french_success = False

# ==============================================================================
# STEP 4: MERGE PANEL
# ==============================================================================

print("\n\n")
print("#" * 70)
print("# STEP 4/4: MERGE FINAL PANEL")
print("#" * 70)

try:
    import merge_final_panel
    merge_final_panel.main()
    merge_success = True
except Exception as e:
    print(f"\n✗ Error: Panel merge failed: {e}")
    merge_success = False

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================

print("\n\n")
print("="*70)
print("PIPELINE EXECUTION SUMMARY")
print("="*70)

status_symbol = lambda x: "✓" if x else "✗"

print(f"\n{status_symbol(michigan_success)} Michigan Consumer Sentiment")
print(f"{status_symbol(aaii_success)} AAII Investor Sentiment")
print(f"{status_symbol(french_success)} Ken French Factors")
print(f"{status_symbol(merge_success)} Final Panel Merge")

if all([french_success, merge_success]):
    print("\n" + "="*70)
    print("✓ DATA PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nYour analysis panel is ready at:")
    print("  data/final/analysis_panel.csv")
    
    if not michigan_success or not aaii_success:
        print("\nNote: Some sentiment data may need manual download.")
        print("See individual script messages above for instructions.")
else:
    print("\n" + "="*70)
    print("⚠ PIPELINE COMPLETED WITH WARNINGS")
    print("="*70)
    print("\nSome steps failed. Please review error messages above.")
    print("\nYou can run individual scripts separately:")
    print("  python code/fetch_michigan_sentiment.py")
    print("  python code/fetch_aaii_sentiment.py")
    print("  python code/fetch_french_factors.py")
    print("  python code/merge_final_panel.py")

print("\n" + "="*70)
