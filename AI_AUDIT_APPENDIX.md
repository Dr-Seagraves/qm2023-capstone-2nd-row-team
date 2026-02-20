# AI Audit Appendix

## 1. AI Tools Used

**Tool Name**: GitHub Copilot (Claude Sonnet 4.5 model)   
**Primary Functions Used**:
- Code generation (Python scripts)
- Debugging assistance (error diagnosis)
- Documentation generation (markdown files, docstrings)
- Command-line help (bash commands, git operations)

## 2. Detailed AI Use Log (Disclose)
We used AI to help us clean and load the data and further explain the prompt. 
### 2.1 Code Generation Tasks

#### **Task 1: FRED API Integration Script**
**File**: `code/fetch_michigan_sentiment.py`

**Prompt **: 
> "Help me create a Python code to download Michigan Consumer Sentiment data from FRED API using fredapi library. Get data from 2004-2024."

**AI-Generated Code** (initial):
```python
from fredapi import Fred
import pandas as pd

api_key = "50023fd424a7ec3070a97a36dc325fab"
fred = Fred(api_key=api_key)

# Download Michigan Consumer Sentiment
data = fred.get_series('UMCSENT', observation_start='2004-01-01')
df = data.to_frame(name='sentiment')
df.to_csv('data/processed/michigan_sentiment.csv')


#### **Task 2: Kenneth French Data Download**
**File**: `code/fetch_french_factors.py`

**Prompt**: 
> "Download Fama-French factor data from Ken French Data Library at Dartmouth"

**AI-Generated Code** (initial):
```python
import pandas as pd
import urllib.request
import zipfile

# Download 3-factor model
url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
urllib.request.urlretrieve(url, 'french_factors.zip')

# Extract and read
with zipfile.ZipFile('french_factors.zip', 'r') as z:
    z.extractall('data/raw/')
    
df = pd.read_csv('data/raw/F-F_Research_Data_Factors.CSV')
``

#### **Task 3: AAII Excel Processing**

**Prompt**: 
> "Process the uploaded sentiment.xls file to extract AAII weekly sentiment data"

**AI-Generated Code

---

#### **Task 4: Merging Datasets**

**Prompt**: 
> "Merge the three processed datasets (Michigan, AAII, French) into a single monthly panel"

**AI-Generated Code** (initial):
```python
michigan = pd.read_csv('data/processed/michigan_sentiment.csv')
aaii = pd.read_csv('data/processed/aaii_sentiment.csv')
french = pd.read_csv('data/processed/french_factors.csv')

panel = michigan.merge(aaii, on='date').merge(french, on='date')
panel.to_csv('data/final/analysis_panel.csv', index=False)
```

**Prompt**: 
> "Generate a comprehensive data quality report documenting data sources, cleaning decisions, merge strategy, and reproducibility"

**AI-Generated Content**:
- Well-structured sections (TOC, executive summary, technical detail)
- Included code snippets and examples
- Generic justifications (e.g., "Clean data is important")
- Missed economic rationale (e.g., why last-of-month aggregation vs. average)

**Human Enhancements**:
- Added economic justifications for all cleaning decisions
- Included before/after counts for all transformations
- Added ethical considerations section (data loss, representativeness)
- Added research questions based on dataset






