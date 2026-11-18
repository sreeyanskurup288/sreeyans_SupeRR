# Day 4 — Pressure Classification and Labels

## Objective
Translate match context into transparent pressure labels for later player-performance analysis.

## Pressure components

Separate two concepts:

- **Practical pressure:** pressure created by match stage, required rate, wickets in hand, score state, and limited deliveries.
- **Desperation pressure:** late-chase or must-win situations where the team has little margin for error.

## Tasks

1. Build stage-pressure weights for league matches, knockouts, finals, and World Cup/T20I contexts.
2. Add chase pressure using runs required, balls remaining, and required run rate.
3. Add wicket and innings-phase pressure.
4. Keep practical and desperation pressure as separate components.
5. Combine components into a calibrated 0–100 pressure score.
6. Define and test pressure labels and sensitivity thresholds.
7. Inspect high-pressure examples manually.

## Deliverables

- `scripts/day4_pressure_labels.py`.
- Pressure labels and examples under `outputs/day4/`.
- Sensitivity notes explaining the calibrated stage points.

## Completion check

Labels should be interpretable, desperation should occur in plausible late or high-stakes states, and the score should not be dominated by one arbitrary rule.