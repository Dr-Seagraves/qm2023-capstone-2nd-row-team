"""
Quick visualization of downloaded Michigan sentiment data
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load the data transfer Michigan sentiment
df = pd.read_csv('data/processed/michigan_sentiment.csv')
df['date'] = pd.to_datetime(df['date'])

# Create visualization
plt.figure(figsize=(14, 6))
plt.plot(df['date'], df['sentiment_michigan_ics'], linewidth=2, color='#2E86AB')
plt.title('University of Michigan Consumer Sentiment Index (2004-2024)', 
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Index Value', fontsize=12)
plt.grid(True, alpha=0.3, linestyle='--')
plt.axhline(y=df['sentiment_michigan_ics'].mean(), color='red', 
            linestyle='--', alpha=0.5, label=f'Mean: {df["sentiment_michigan_ics"].mean():.1f}')

# Add recession shading (2008 Financial Crisis, 2020 COVID)
plt.axvspan(pd.Timestamp('2008-01-01'), pd.Timestamp('2009-06-30'), 
            alpha=0.2, color='gray', label='2008-09 Recession')
plt.axvspan(pd.Timestamp('2020-02-01'), pd.Timestamp('2020-04-30'), 
            alpha=0.2, color='gray', label='2020 COVID Recession')

plt.legend(loc='best', fontsize=10)
plt.tight_layout()

# Save figure
plt.savefig('results/figures/michigan_sentiment_timeseries.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved to: results/figures/michigan_sentiment_timeseries.png")

# Display summary statistics
print("\n" + "="*60)
print("MICHIGAN CONSUMER SENTIMENT - SUMMARY STATISTICS")
print("="*60)
print(f"\nTime Period: {df['date'].min().strftime('%B %Y')} to {df['date'].max().strftime('%B %Y')}")
print(f"Total Observations: {len(df)} months")
print(f"\nSentiment Index Statistics:")
print(f"  Mean:     {df['sentiment_michigan_ics'].mean():.2f}")
print(f"  Median:   {df['sentiment_michigan_ics'].median():.2f}")
print(f"  Std Dev:  {df['sentiment_michigan_ics'].std():.2f}")
print(f"  Min:      {df['sentiment_michigan_ics'].min():.2f} ({df.loc[df['sentiment_michigan_ics'].idxmin(), 'date'].strftime('%B %Y')})")
print(f"  Max:      {df['sentiment_michigan_ics'].max():.2f} ({df.loc[df['sentiment_michigan_ics'].idxmax(), 'date'].strftime('%B %Y')})")
print("\n" + "="*60)

plt.show()
