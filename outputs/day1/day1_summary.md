# Day 1 Summary

- CSV files inventoried: 6
- Matches in joined context table: 883
- Delivery rows in source pack: 200999

## Matches by analysis group and stage

| analysis_group   | stage_group   |   matches |
|:-----------------|:--------------|----------:|
| IPL              | Final         |         5 |
| IPL              | Knockout      |        15 |
| IPL              | League        |       351 |
| Other T20        | Final         |         2 |
| Other T20        | Knockout      |         4 |
| Other T20        | League        |        24 |
| T20I             | Final         |         5 |
| T20I             | League        |       245 |
| T20I             | Other         |       232 |

## Notes

- `analysis_group` separates IPL, T20I, and other T20 competitions.
- `stage_group` uses the supplied `stage` and `knock_out` fields.
- Delivery-level score and legal-ball reconstruction is intentionally deferred to a later step.
