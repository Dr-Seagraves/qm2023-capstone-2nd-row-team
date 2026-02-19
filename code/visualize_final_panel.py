"""
Create Overview Visualization of Final Panel Dataset
====================================================
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# Load the final panel
df = pd.read_csv('data/final/analysis_panel.csv')
df['date'] = pd.to_datetime(df['date'])

# Create comprehensive visualization
fig, axes = plt.subplots(3, 1, figsize=(14, 12))

# Plot 1: Michigan Consumer Sentiment
ax1 = axes[0]
ax1.plot(df['date'], df['sentiment_michigan_ics'], linewidth=2, color='#2E86AB', label='Michigan Sentiment')
ax1.set_title('University of Michigan Consumer Sentiment Index (2004-2024)', fontsize=14, fontweight='bold')
ax1.set_ylabel('Index Value', fontsize=11)
ax1.axhline(y=df['sentiment_michigan_ics'].mean(), color='red', linestyle='--', alpha=0.5, linewidth=1)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.legend(loc='best')

# Plot 2: AAII Investor Sentiment
ax2 = axes[1]
ax2.plot(df['date'], df['bullish_pct'], linewidth=1.5, color='#06A77D', label='Bullish %', alpha=0.8)
ax2.plot(df['date'], df['bearish_pct'], linewidth=1.5, color='#D62246', label='Bearish %', alpha=0.8)
ax2.plot(df['date'], df['neutral_pct'], linewidth=1.5, color='#F77F00', label='Neutral %', alpha=0.6)
ax2.set_title('AAII Investor Sentiment Survey (2004-2024)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Percentage', fontsize=11)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.legend(loc='best')

# Plot 3: Market Returns and Factors
ax3 = axes[2]
ax3.plot(df['date'], df['mkt_ret'].cumsum(), linewidth=2, color='#1B4965', label='Cumulative Market Return')
ax3.set_title('Cumulative Market Return (Ken French Data, 2004-2024)', fontsize=14, fontweight='bold')
ax3.set_ylabel('Cumulative Return (%)', fontsize=11)
ax3.set_xlabel('Date', fontsize=11)
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.legend(loc='best')
ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=0.8)

# Format x-axis for all plots
for ax in axes:
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('results/figures/final_panel_overview.png', dpi=300, bbox_inches='tight')
print("✓ Saved comprehensive visualization to: results/figures/final_panel_overview.png")

# Print dataset summary
print("\n" + "="*70)
print("FINAL PANEL DATASET SUMMARY")
print("="*70)
print(f"\nDimensions: {len(df)} rows × {len(df.columns)} columns")
print(f"Period: {df['date'].min().strftime('%B %Y')} to {df['date'].max().strftime('%B %Y')}")
print(f"\nVariables Included:")
print("\n  Michigan Sentiment:")
print(f"    • sentiment_michigan_ics (Consumer Sentiment Index)")
print(f"\n  AAII Investor Sentiment:")
print(f"    • bullish_pct (% Bullish investors)")
print(f"    • neutral_pct (% Neutral investors)")
print(f"    • bearish_pct (% Bearish investors)")
print(f"    • bull_bear_spread (Bullish - Bearish)")
print(f"\n  Ken French Factors:")
print(f"    • mkt_rf (Market excess return)")
print(f"    • mkt_ret (Total market return)")
print(f"    • smb (Size factor)")
print(f"    • hml (Value factor)")
print(f"    • rmw (Profitability factor)")
print(f"    • cma (Investment factor)")
print(f"    • rf (Risk-free rate)")

print(f"\nData Quality:")
print(f"  • Complete monthly observations: {len(df)}/252 months")
print(f"  • Missing values: {df.isnull().sum().sum()}")
print(f"  • All three data sources successfully merged!")

print("\n" + "="*70)
print("READY FOR ANALYSIS!")
print("="*70)
print("\nTo load and use the data:")
print("""
import pandas as pd
df = pd.read_csv('data/final/analysis_panel.csv')
df['date'] = pd.to_datetime(df['date'])
""")

plt.show()
