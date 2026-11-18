# Day 3 — Delivery-Level Match State Pipeline

## Objective
Create a delivery-level table describing the match situation immediately before every delivery.

## Features

Calculate or attach:

- `score_before`
- `wickets_before`
- `legal_balls_before`
- `legal_balls_remaining`
- `target`
- `runs_required`
- `required_run_rate`
- `innings_phase`
- `current_run_rate`
- `projected_final_score`
- Competition, format, season, stage, and knockout context

## Tasks

1. Sort deliveries correctly within every innings.
2. Apply the approved numeric extras rule uniformly.
3. Track score, wickets, and legal balls cumulatively.
4. Calculate first-innings and chase-specific state variables.
5. Add phase labels such as powerplay, middle, and death overs.
6. Attach match metadata and validate edge cases.
7. Save a sample state table and match-innings summary.

## Deliverables

- `scripts/day3_match_state.py`.
- Delivery-level state output under `outputs/day3/`.
- Match-state summary and quality checks.

## Completion check

There should be no missing competition context, negative legal-ball values, or impossible targets in the validated output.