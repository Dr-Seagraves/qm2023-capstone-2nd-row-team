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

## Milestone 3

## Task: Converting Data to Long-Format
- Files:
    - analysis_panel_wide.csv
    - analysis_panel.csv
    - Reverification of the files in the code, data, and results folders
- AI Help:
    - Prompt: "Can you convert this data into long format? Make sure to fix any issues in other data or graphs this change may cause"
    - It converted the data into long format and then adjusted other files accordingly
- Human verification: 
    - We made sure the data was converted into long format appropriately 

## Task: FE and DiD

- Files:
    - README.md
    - generate_m3_analysis.py
    - FE market model table: m3_market_fe_results.csv
    - Entity FE table: m3_entity_fe_results.csv
    - DiD table: m3_did_results.csv
    - Treated vs control trends: m3_treated_vs_control_trends.png
    - DiD coefficient plot: m3_did_coefficients.png
    - Market model fit plot: m3_market_model_fit.png
    - M3_interpretation.md
    - M3_interpretation.m
- Prompts: 
    - "Help me create an entity fixed effects regression model for the data and also do a difference in difference regression that looks at the shocks of COVID and the 2008 financial crisis on the data if the tests can be applied. Use a bunch of easily-understandable economic interpretation so we can understand the results in M3_interpretation.md. Make sure to include graphs and plots. Make sure everything is completed in the README M3.pdf and that it satisfies the rubric M3.pdf. Do not fill out the AI audit (and ignore that section on the rubric)"
    - "Yes, please do that. You may use an OCR tool"
    - "Please do so"
- AI Help:
    - Implemented the full M3 econometrics workflow and generated all requested deliverables (entity fixed effects, DiD for 2008/COVID shocks, plots, and plain-language interpretation). It also verified against the rubric
    - Added two-way FE style Model A with entity and time fixed effects plus clustered SE by entity in generate_m3_analysis.py.
    - Updated DiD to use clustered SE by entity in generate_m3_analysis.py.
    - Added diagnostics:
        - Breusch-Pagan table: m3_bp_test_results.csv
        - VIF table: m3_vif_results.csv
    - Residual plots: m3_residuals_vs_fitted.png, m3_residuals_qq.png, m3_residuals_hist.png
    - Added 3 robustness checks and comparison output: m3_robustness_checks.csv.
    - Added publication-style side-by-side model table with stars/notes row: m3_model_comparison_table.csv.
    - Added deliverable-name wrapper script: capstone_models.py.
    - Updated README run instructions and output list in README.md.
- Human verfication:
    - We looked over the output and regressions to verify, noticed some errors, and either manually changed things or reprompted AI (disclosed in this same section)

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






