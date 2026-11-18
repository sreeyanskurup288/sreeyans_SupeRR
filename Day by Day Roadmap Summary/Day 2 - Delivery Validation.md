# Day 2 — Delivery Semantics and Score Validation

## Objective
Validate what each ball-by-ball field means before calculating pressure or performance metrics.

## Tasks

1. Inspect `runs`, `extras1_runs`, `extras_2_runs`, `extras_type`, and wicket fields.
2. Review representative wides, byes, leg-byes, no-balls/oversteps, penalties, boundaries, and wickets.
3. Confirm the corrected numeric extras interpretation from the updated CSV.
4. Use the approved score rule: `total_runs = runs + extras1_runs`.
5. Define legal-delivery logic and document known limitations.
6. Select one uninterrupted match for manual reconstruction.
7. Reconstruct innings totals, wickets, and sample match summaries.

## Deliverables

- `scripts/day2_delivery_validation.py`.
- Delivery-semantics notes under `outputs/day2/`.
- Sample score and wicket reconstruction.
- Validation output documenting the approved extras rule.

## Completion check

The reconstructed sample should be consistent with the selected data interpretation, and the rule must be documented before feature engineering begins.