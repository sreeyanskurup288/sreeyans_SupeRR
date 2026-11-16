# Day 2 Validation Notes

## Findings

- `runs` is consistent with batter runs: it aligns with `is_four` and `is_six` and ranges from 0 to 6.
- `extras_type` identifies wide, leg-bye, bye, overstep, other, and penalty events.
- The revised `extras1_runs` is a numeric extras amount: wides, byes, and leg-byes vary from 1 to 5; oversteps and other extras are 1; the penalty row is 5.
- `extras_2_runs` remains zero/unused in the revised export and is ignored.
- `innings_ball_num` is unique within match and innings, but it counts delivery rows rather than legal balls.
- The default legal-delivery rule for the next stage is to treat `wide` and `Overstep` as illegal, subject to further validation.

## Score reconstruction

The revised export supports numeric score reconstruction using `total_runs = runs + extras1_runs`. `extras_type` remains the category label, while `extras_2_runs` is ignored. This removes the earlier one-run-per-extra fallback.

## Sample match

The script validates match 13511 structurally: delivery sequence, legal/illegal delivery counts, batter runs, numeric extra runs, reconstructed total runs, and wickets by innings.

## Reproduction

```bash
python scripts/day2_delivery_validation.py --input-dir /path/to/data --output-dir outputs/day2
```

## Semantic summary

| category             |   rows |   runs_min |   runs_max | extras1_values   | extras2_values   | legal_delivery_default   |
|:---------------------|-------:|-----------:|-----------:|:-----------------|:-----------------|:-------------------------|
| ordinary_or_no_extra | 189167 |          0 |          6 | 0, 1             | 0, 1             | True                     |
| wide                 |   7714 |          0 |          0 | 1, 2, 3, 4, 5    | 0                | False                    |
| legbyes              |   2748 |          0 |          1 | 0, 1, 2, 3, 4, 5 | 0                | True                     |
| byes                 |    529 |          0 |          0 | 1, 2, 3, 4, 5    | 0                | True                     |
| overstep             |    576 |          0 |          6 | 1                | 0, 1, 4          | False                    |
| other                |    264 |          0 |          6 | 1                | 0, 1, 4          | True                     |
| penalty              |      1 |          0 |          0 | 5                | 0                | True                     |

## Sample match validation

|   match_id |   innings |   delivery_rows |   first_innings_ball_num |   last_innings_ball_num |   max_overid |   legal_deliveries |   illegal_deliveries |   runs_off_bat |   extra_events |   extras2_ignored_sum |   wickets |   extra_runs |   total_runs |
|-----------:|----------:|----------------:|-------------------------:|------------------------:|-------------:|-------------------:|---------------------:|---------------:|---------------:|----------------------:|----------:|-------------:|-------------:|
|      13511 |         1 |             121 |                        1 |                     121 |           20 |                118 |                    3 |            100 |              3 |                     0 |        10 |            3 |          103 |
|      13511 |         2 |             103 |                        1 |                     103 |           18 |                103 |                    0 |             99 |              2 |                     0 |         1 |            5 |          104 |

