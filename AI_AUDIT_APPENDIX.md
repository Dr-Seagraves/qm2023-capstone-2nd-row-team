# AI Audit Appendix

## 1. AI Tools Used
- M2 USE OF AI: 
- Tool: GitHub Copilot (used for coding and writing support)
- Primary use cases:
    - Python code drafting and refactoring
    - Debugging and error diagnosis
    - Markdown/report drafting and editing
    - Workflow support for reproducible analysis

## 2. Scope of AI Assistance

- AI was used as an assistant, not a decision-maker.
- All final code, figures, and written interpretations were reviewed by team members.
- Economic interpretation, variable choices, and modeling rationale were finalized by the team.

## 3. M1 AI Use Log (Data Pipeline)

### Task: FRED Michigan Sentiment Fetch
- File: `code/fetch_michigan_sentiment.py`
- AI help: Starter structure for API call, date filtering, and CSV export.
- Human verification:
    - Confirmed series ID and time range.
    - Validated row counts and date alignment.

### Task: Ken French Factor Download and Parsing
- File: `code/fetch_french_factors.py`
- AI help: Drafted download/parsing flow for French library files.
- Human verification:
    - Checked parsing logic against source file format.
    - Confirmed factors were scaled and typed correctly.

### Task: AAII Processing and Merge
- Files: `code/process_aaii_excel.py`, `code/merge_final_panel.py`
- AI help: Provided cleaning/merge scaffolding and aggregation ideas.
- Human verification:
    - Confirmed monthly aggregation choice.
    - Checked join keys, frequency matching, and missing values.

## 4. M2 AI Use Log (EDA Dashboard)

### Task: Build EDA Deliverables and Notebook Structure
- Files:
    - `code/generate_m2_deliverables.py`
    - `capstone_eda.ipynb`
    - `M2_EDA_summary.md`
- AI help:
    - Proposed section flow for M2 notebook.
    - Generated plotting code patterns for required visuals.
    - Drafted summary wording for findings and hypotheses.
- Human verification:
    - Confirmed plot choices match assignment requirements.
    - Reviewed each caption for economic relevance.
    - Checked file paths, output locations, and reproducibility.
 
### Task: HTML Dashboard
- Files:
    - M2_interactive_dashboard_v2.html
    - M2_EDA_summary.md
 - AI Help
    - AI wrote the HTML code
 - Human verification:
    - We had AI re-write the code several times because the HTML dashboard was not very readable at first. 

## 5. Validation and Quality Control

- Re-ran analysis from raw M1 panel output to verify reproducibility.
- Confirmed figures save to `results/figures/` with `M2_` filename prefix.
- Verified notebook can execute top-to-bottom after kernel restart.
- Cross-checked key findings in the summary against computed outputs.

## 6. Known Risks and Mitigations

- Risk: AI-generated code may include incorrect defaults or assumptions.
    - Mitigation: Manual code review and output validation.
- Risk: AI-generated text can overstate causal conclusions.
    - Mitigation: Team edits to keep interpretations correlational and testable.
- Risk: AI may omit edge-case checks.
    - Mitigation: Added data quality checks and explicit diagnostics.

## 7. Human Responsibility Statement

The team is fully responsible for all submitted code, figures, and written claims. AI assistance was used for productivity support, while final methodological and interpretive decisions were made by the team.






