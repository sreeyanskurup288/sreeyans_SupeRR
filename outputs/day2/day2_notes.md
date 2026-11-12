# Day 2 Validation Notes

## Findings

- `runs` is consistent with batter runs: it aligns with `is_four` and `is_six` and ranges from 0 to 6.
- `extras_type` identifies wide, leg-bye, bye, overstep, other, and penalty events.
- `extras1_runs` is not a usable extra-run amount: it acts like a category code (ordinary deliveries use 6; wide 2; leg-bye 3; bye 4; overstep 1; other 5; penalty 7).
- `extras_2_runs` is ignored provisionally, pending a later discrepancy review.
- `innings_ball_num` is unique within match and innings, but it counts delivery rows rather than legal balls.
- The default legal-delivery rule for the next stage is to treat `wide` and `Overstep` as illegal, subject to further validation.

## Exact-score limitation

For the current prototype, every nonblank `extras_type` event is provisionally awarded one team run. This intentionally does not capture five wides or multi-run byes/leg-byes. `extras1_runs` is treated as a type ID and `extras_2_runs` is ignored. If later checks reveal a discrepancy, this rule will be revisited.

## Sample match

The script validates match 13511 structurally: delivery sequence, legal/illegal delivery counts, batter runs, extra events, and wickets by innings. This is a complete two-innings sample for checking the delivery-state pipeline, while the score caveat above remains applicable.

## Reproduction

```bash
python scripts/day2_delivery_validation.py --input-dir /path/to/data --output-dir outputs/day2
```

## Semantic summary

| category             |   rows |   runs_min |   runs_max |   extras1_values | extras2_values   | legal_delivery_default   |
|:---------------------|-------:|-----------:|-----------:|-----------------:|:-----------------|:-------------------------|
| ordinary_or_no_extra | 189167 |          0 |          6 |                6 | 0, 1             | True                     |
| wide                 |   7714 |          0 |          0 |                2 | 0                | False                    |
| legbyes              |   2748 |          0 |          1 |                3 | 0                | True                     |
| byes                 |    529 |          0 |          0 |                4 | 0                | True                     |
| overstep             |    576 |          0 |          6 |                1 | 0, 1, 4          | False                    |
| other                |    264 |          0 |          6 |                5 | 0, 1, 4          | True                     |
| penalty              |      1 |          0 |          0 |                7 | 0                | True                     |

## Sample match validation

|   match_id |   innings |   delivery_rows |   first_innings_ball_num |   last_innings_ball_num |   max_overid |   legal_deliveries |   illegal_deliveries |   runs_off_bat |   extra_events |   extras2_ignored_sum |   wickets |   provisional_extra_runs |   provisional_total_runs |
|-----------:|----------:|----------------:|-------------------------:|------------------------:|-------------:|-------------------:|---------------------:|---------------:|---------------:|----------------------:|----------:|-------------------------:|-------------------------:|
|      13511 |         1 |             121 |                        1 |                     121 |           20 |                118 |                    3 |            100 |              3 |                     0 |        10 |                        3 |                      103 |
|      13511 |         2 |             103 |                        1 |                     103 |           18 |                103 |                    0 |             99 |              2 |                     0 |         1 |                        2 |                      101 |

