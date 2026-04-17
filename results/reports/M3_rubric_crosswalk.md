# M3 Rubric Crosswalk (OCR-Based)

Date: 2026-04-17
Method: OCR extraction from `rubric M3.pdf` and `README M3.pdf`.

## Source documents parsed
- `tmp/m3_pdf_text/rubric_m3.txt`
- `tmp/m3_pdf_text/readme_m3.txt`

## Submission evidence reviewed
- `code/generate_m3_analysis.py`
- `M3_interpretation.md`
- `results/reports/M3_interpretation.md`
- `README.md`
- `results/tables/m3_market_fe_results.csv`
- `results/tables/m3_entity_fe_results.csv`
- `results/tables/m3_did_results.csv`
- `results/figures/m3_treated_vs_control_trends.png`
- `results/figures/m3_did_coefficients.png`
- `results/figures/m3_market_model_fit.png`

## Rubric line-item mapping

### 1) Model Specification (15 points)
- Model A FE with entity and time FE (`entity_effects=True`, `time_effects=True`): PARTIAL
Evidence: `code/generate_m3_analysis.py` estimates FE-style models with `C(variable)` in panel models and month fixed effects in market model. The DiD model uses `C(date)`.
Gap: Model A is not implemented as canonical two-way panel FE with explicit entity + full time FE on a panel outcome.
- Model B appropriate (DiD/ARIMA/ML): YES
Evidence: DiD specification with treatment-control interactions for GFC and COVID shocks.
- Variable selection economically sensible and tied to M2: PARTIAL
Evidence: lagged sentiment terms and Fama-French controls are included.
Gap: explicit M2-derived lag-selection justification is limited in-code.
- Clustered SEs used correctly: NO
Evidence: models use `cov_type="HC1"` (robust heteroskedastic SE), not clustered by entity.
- Code structure/reproducibility: YES
Evidence: end-to-end runnable script; outputs saved consistently.

Estimated range for this section: 9 to 12 / 15 (Satisfactory).

### 2) Diagnostics & Robustness (12 points)

Diagnostics (6)
- Heteroskedasticity test or residual-vs-fitted diagnostic: PARTIAL
Evidence: market fit plot exists, but no explicit Breusch-Pagan result or dedicated residual diagnostic section.
- Multicollinearity (VIF): NO
Evidence: no VIF calculation in script or report.
- Residual normality plot (Q-Q or histogram) and interpretation: NO
Evidence: not included.
- Diagnostics interpreted: PARTIAL
Evidence: some interpretation in memo, but not formal diagnostics interpretation.

Robustness checks (6)
- At least 3 robustness checks (alt lags, exclusion windows, subsamples, placebo): NO
Evidence: no dedicated robustness-check block with comparative results.
- Results compared and implications discussed: NO

Estimated range for this section: 1 to 4 / 12 (Needs Improvement).

### 3) Interpretation & Economic Reasoning (18 points)

Coefficient interpretation (10)
- Economic interpretation, sign/significance, magnitudes, non-significant terms: YES (mostly)
Evidence: `M3_interpretation.md` provides plain-language sign and significance interpretation for major terms.
Gap: magnitude-to-real-world scaling could be deeper for some coefficients.

Economic mechanisms/theory (8)
- Mechanisms, theory consistency, heterogeneity, alternatives: PARTIAL
Evidence: memo includes causal caveat and interpretation language.
Gap: limited explicit mapping to named theory channels and alternative explanations.

Estimated range for this section: 12 to 16 / 18 (Satisfactory to Excellent boundary).

### 4) Presentation & Documentation (5 points)

Regression tables (3)
- Publication-ready columns: YES
Evidence: CSV tables include variable, coefficient, SE, t-stat, p-value, CI.
- Side-by-side comparison table and notes row (FE/time FE/clustered/N/R2): PARTIAL/NO
Evidence: outputs are separate CSVs; no combined comparison table with notes row.
- Significance stars: PARTIAL
Evidence: stars appear in memo text, not in CSV table columns.

Code & memo quality (2)
- Code clean/modular/reproducible and memo complete: YES
Evidence: script modularized into functions; memo present and complete.

Estimated range for this section: 3 to 4 / 5.

### AI Audit Appendix requirement (Pass/Fail)
- Required by rubric for credit: NOT SATISFIED currently.
Evidence: rubric states missing appendix => 0/50.
Project note: This was intentionally not completed per user instruction.

## README M3 instructions compliance check
From `README M3.pdf` deliverables:
- Script should be named `capstone_models.py`: NOT SATISFIED (current script is `code/generate_m3_analysis.py`).
- Must include sections for diagnostics and robustness checks: PARTIAL/NOT SATISFIED.
- Save tables and figures into configured directories: SATISFIED.
- Include Model A + one Model B: SATISFIED.

## Estimated score and risk
- Technical rubric components (excluding AI-audit pass/fail policy): approximately 25 to 36 / 50.
- Primary point losses likely from diagnostics/robustness and non-clustered SE.
- Policy risk: if AI audit pass/fail is enforced strictly, missing appendix can trigger 0/50 regardless of technical quality.

## High-impact fixes to maximize score quickly
1. Add clustered SEs for panel entity-based models (or justify if infeasible for a given spec).
2. Add diagnostics section with:
   - Breusch-Pagan test,
   - VIF table,
   - residual Q-Q and residual-vs-fitted plots,
   - brief interpretations.
3. Add 3 robustness checks with comparison table:
   - alternative lags,
   - exclusion of crisis windows,
   - placebo DiD in pre-period.
4. Add a publication-ready combined model comparison table with notes row and significance stars.
5. Add lightweight wrapper script named `capstone_models.py` that calls existing pipeline.
6. If policy constraints allow, complete AI audit appendix (rubric indicates this is mandatory for credit).

## Bottom line
Current deliverables satisfy the core request (FE + DiD + plots + interpretation), but they do not yet meet several top-rubric criteria for full points, especially diagnostics, robustness, clustered SEs, and the rubric's pass/fail AI-audit policy.

## Post-fix update (implemented on 2026-04-17)
- Added two-way FE style Model A on long panel with `C(variable) + C(date)` and clustered SE by entity (`variable`).
- Added clustered SEs for DiD model.
- Added diagnostics outputs:
   - `results/tables/m3_bp_test_results.csv`
   - `results/tables/m3_vif_results.csv`
   - `results/figures/m3_residuals_vs_fitted.png`
   - `results/figures/m3_residuals_qq.png`
   - `results/figures/m3_residuals_hist.png`
- Added three robustness checks with comparison output:
   - `results/tables/m3_robustness_checks.csv`
- Added publication-style side-by-side comparison table with stars and notes row:
   - `results/tables/m3_model_comparison_table.csv`
- Added deliverable-name wrapper script:
   - `code/capstone_models.py`

### Revised estimated score/risk
- Technical rubric components (excluding AI-audit pass/fail policy): approximately 40 to 47 / 50.
- Main remaining risk: rubric-specific requirement for AI audit appendix completeness (policy-level risk).
