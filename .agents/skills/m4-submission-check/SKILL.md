---
name: m4-submission-check
description: "Use when preparing, reviewing, or polishing the QM2023 Milestone 4 final deliverable. Triggers include: final deliverable, M4, final investment memo, final memo, individual addendum, submission checklist, formatting review, interpretable writing, well written memo, publication-ready tables, figure review, AI audit appendix, PDF export, and final submission readiness."
argument-hint: "Describe the artifact to review, such as the team memo source, PDF, individual addendum, or the full M4 submission"
---

# M4 Submission Check

Use this skill to turn the Milestone 4 handout into a concrete review workflow for this repository.

## What This Skill Produces

- A compliance check against the M4 memo and addendum requirements
- A writing-quality pass aimed at a non-technical decision-maker
- A consistency check between the memo narrative and the repo's actual tables, figures, and model outputs
- A final submission-readiness checklist for filenames, PDFs, and required appendices

## Repo-Specific Anchors

Start from these references before suggesting edits:

- [M4 requirements](./references/m4-requirements.md)
- [Current repo deliverable anchors](./references/repo-deliverable-anchors.md)

## When To Use

Use this skill when the user asks to:

- create or polish the final investment memo
- verify the final deliverable formatting
- check whether everything required for submission is present
- make the memo more interpretable or better written
- review the individual addendum
- confirm the final PDFs match the repository evidence

## Procedure

1. Identify the artifact and review mode.
   - Team memo: apply the full M4 memo rubric.
   - Individual addendum: apply the one-page individual checklist.
   - Full submission: review both PDFs plus repository consistency.
   - Source file available: edit the source before export.
   - PDF only: review layout/content first, then ask for the editable source if substantive fixes are needed.

2. Lock the requirement baseline.
   - Use the M4 handout as the controlling requirement for structure, page targets, section coverage, and submission rules.
   - Use the repo anchors to determine which current outputs are the real evidence base.
   - In this repository, prefer the M3v2 firm-panel deliverables when the final memo needs a panel-based main story.

3. Run the structural compliance pass before doing prose polish.
   - Team memo must include: Executive Summary, Methodology, Results, Conclusions and Recommendations, References, and Appendix: AI Audit.
   - Individual addendum must include: Personal Contribution, One Defended Decision, One Key Limitation, and AI Audit Notes if needed.
   - Check target lengths: team memo 5-7 pages, addendum exactly 1 page.
   - Check output format: professional PDF, not Word or a link.

4. Run the evidence traceability pass.
   - Every numerical claim should map to an existing table, figure, or model output in the repository.
   - Confirm the memo contains one main model table and one alternative-specification table.
   - Confirm the memo contains one key visualization and one diagnostic figure.
   - If numbers in the prose disagree with repo outputs, fix the numbers before editing style.
   - If the memo cites an outdated M3 artifact while the repo's live analysis is M3v2, flag and correct that mismatch.

5. Run the interpretation pass for non-technical readers.
   - Convert coefficients into plain-English economic magnitude.
   - Define variables and acronyms before using them repeatedly.
   - Replace methodological jargon with business-language summaries when possible.
   - Keep causal claims narrower than the evidence supports.
   - Recommendations must tell the reader what action to take, not just what the model found.

6. Run the formatting and presentation pass.
   - No raw console output pasted into the memo.
   - Tables must be labeled, readable, and publication-ready.
   - Figures should be high resolution and clearly titled.
   - Section headings should match the required structure.
   - References must include data sources, URLs, and any cited papers.

7. Run the caveat and honesty pass.
   - Check that assumptions and limitations are explicit.
   - Check that omitted-variable, external-validity, and design-limit concerns are acknowledged.
   - If the fixed-effects or DiD framing is used, verify the memo states the practical identification caveat in plain language.
   - Keep the AI audit appendix present and substantive.

8. Run the submission pass.
   - Team memo filename should match `Final_Investment_Memo.pdf` unless the instructor has approved a different convention.
   - Individual files should follow `Individual_Addendum_[YourName].pdf`.
   - Confirm team-member names are present.
   - Confirm the intended files are committed to the shared repository and ready for push to `main`.

## Decision Rules

- If a required section is missing, add or outline that section before doing sentence-level polish.
- If the memo is structurally complete but hard to follow, prioritize Executive Summary, Results interpretation, and Conclusions.
- If a claim is stronger than the model supports, soften the prose rather than overstating certainty.
- If the story conflicts with the repo outputs, update the story to match the evidence unless the user is explicitly re-running analysis.
- If multiple analysis branches exist in the repository, use the branch that best fits the M4 requirement for a coherent, reproducible final memo. In this repo that is usually the M3v2 pipeline.
- If the user is using an alternative dataset or audience, keep the required sections but adapt the recommendation framing away from "investment committee" language as allowed by the handout.

## Completion Standard

Do not call the deliverable ready until all of the following are true:

- Required sections and page targets are satisfied
- Results, tables, and figures match the repository evidence
- Recommendations are specific and actionable
- Caveats are honest and substantive
- Writing is understandable to a non-technical reader
- PDF naming and submission requirements are satisfied

## Suggested Output Format For Reviews

When using this skill, report back in this order:

1. Missing or non-compliant items
2. Evidence mismatches or reproducibility risks
3. Writing and interpretation fixes
4. Submission-ready checklist status