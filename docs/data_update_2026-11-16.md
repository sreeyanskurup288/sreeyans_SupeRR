# Ball-by-ball data update — 2026-11-16

The uploaded `6af855c0e8386_ball_by_ball.csv` was compared with the previous local source before replacement.

## File-level comparison

- Rows: unchanged at 200,999.
- Columns: unchanged at 33.
- Match IDs: unchanged at 867.
- Delivery keys (`match_id`, `innings`, `innings_ball_num`): unchanged.
- SHA-256 of updated source: `01e2b4379edfbab6a6e456d304cb3c70f554cb312ef93d9588f3f32a82cb396e`.

## Substantive changes

- `extras1_runs` is now a numeric extras amount instead of the previous category-like encoding.
- Wides now range from 1 to 5 runs.
- Byes now range from 1 to 5 runs.
- Leg-byes now range from 0 to 5 runs.
- Overstep/no-ball rows are 1 run.
- `other` rows are 1 run.
- The penalty row is 5 runs.
- 24 `striker_name` values and 33 `non_striker_name` values were corrected, including `AHT Donald` → `Aneurin Donald`.
- `extras_2_runs` remains unused because it is zero in the extra rows inspected.

## New score rule

```text
total_runs = runs + extras1_runs
```

The earlier one-run-per-extra fallback is retired. Day 2–6 scripts and derived outputs were regenerated from the updated source.

The previous local source was preserved outside the repository as:

```text
/home/ubuntu/superr_data/ball_by_ball_previous.csv
```

Raw data is not committed to GitHub.
