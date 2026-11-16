# Day 3 Match-State Notes

## State variables created

- `score_before`: provisional team score before the delivery.
- `wickets_before`: wickets lost before the delivery.
- `legal_balls_before` and `legal_balls_remaining`: based on `wide` and `Overstep` being illegal deliveries.
- `target`: supplied `revised_target` when present; otherwise provisional first-innings total plus one for the chase.
- `runs_required` and `required_run_rate`: calculated for the second innings only.
- `current_run_rate` and `projected_final_score`: calculated from the state before each delivery.
- `innings_phase`: Powerplay, Middle, or Death using 30% and 80% of the available innings balls.

## Uniform extras rule

The revised CSV provides numeric extras in `extras1_runs`. The pipeline now uses `runs + extras1_runs` for total delivery runs; `extras_type` remains the category label and `extras_2_runs` is ignored.

## Reproduction

```bash
python scripts/day3_match_state.py --input-dir /path/to/data --output-dir outputs/day3
```

The committed sample is match `13511`. The script also validates all 1724 match-innings groups and writes a compact summary.
