# Day 5 — Player Metrics Under Pressure

## Objective
Aggregate batting and bowling performance separately in pressure and normal situations.

## Batting metrics

Calculate pressure versus normal performance using appropriate denominators, including runs, balls, strike rate, dismissals, boundary contribution, and sample sizes.

## Bowling metrics

Calculate pressure versus normal performance using wickets, balls, runs conceded, economy, dismissal attribution, and sample sizes. Exclude dismissals that should not be credited to the bowler.

## Tasks

1. Join Day 3 match state and Day 4 pressure labels to deliveries.
2. Aggregate player-by-match and player-level metrics.
3. Separate pressure deliveries from normal deliveries.
4. Track pressure events, pressure matches, innings, and exposure.
5. Check sample-size distributions and missing player identifiers.
6. Re-run after any corrected ball-by-ball data update.

## Deliverables

- `scripts/day5_player_metrics.py`.
- `outputs/day5/batting_metrics.csv`.
- `outputs/day5/bowling_metrics.csv`.
- Sample-size and quality checks.

## Completion check

The outputs must distinguish pressure performance from overall performance and retain enough exposure fields for reliability filtering.