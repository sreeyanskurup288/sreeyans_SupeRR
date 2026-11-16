# Day 5 Player Metrics

## Pressure sample

A delivery is in the pressure segment when the Day 4 `is_practical_pressure` flag is true; all other deliveries form the normal baseline. Batting uses legal deliveries for balls faced and runs off the bat for scoring. Bowling uses legal deliveries, excludes byes/leg-byes/penalty from bowler runs conceded, and credits wickets only for bowler-attributable dismissal types.

## Corrected extras

The updated ball-by-ball CSV provides numeric extras in `extras1_runs`. Day 5 uses `total_runs = runs + extras1_runs` through the Day 3 state builder.

## Outputs

- `batting_metrics.csv`: overall, normal, and pressure batting metrics.
- `bowling_metrics.csv`: overall, normal, and pressure bowling metrics.
- Use `--write-full-labels` only for a local downstream run; raw data and full delivery labels are not committed by default.
