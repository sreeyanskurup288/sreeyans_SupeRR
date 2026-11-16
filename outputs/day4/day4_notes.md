# Day 4 Pressure-Label Notes

## Main rule

Pressure is calculated from the match state before the delivery. Delivery outcomes are not used, preventing outcome leakage.

## Second innings

`second_innings_pressure_score` uses 40 points of required-rate pressure, 25 points of ball-resource pressure, 20 points of wicket-resource pressure, and a stage adjustment of 0 points for League, 3 for Other, 10 for Knockout, and 15 for Final. Practical pressure is a score of at least 75 with positive runs required. Desperation is a practical-pressure delivery with a score of at least 90 and either 18 or fewer legal balls remaining or at least seven wickets already lost.

## First innings

`first_innings_pressure_score` is exploratory because there is no target yet. It uses wickets lost, late-innings resource pressure, projected-score deficit versus the peer scoring environment, and stage pressure. First-innings desperation additionally requires 18 or fewer balls remaining and at least six wickets lost.

## Uniform extras rule

The revised CSV provides numeric extras in `extras1_runs`; total delivery runs are reconstructed as `runs + extras1_runs`. `extras_type` is the category label and `extras_2_runs` is ignored.

## Counts

- Deliveries processed: 200,999
- Second-innings deliveries: 95,234
- First-innings deliveries: 105,727
- Practical-pressure deliveries (combined): 3,040
- Desperation-pressure deliveries (combined): 37

## Reproduction

```bash
python scripts/day4_pressure_labels.py --input-dir /path/to/data --output-dir outputs/day4
```

The full delivery-level labels are intentionally not committed by default; use `--write-full` for a local downstream Day 5 run.
