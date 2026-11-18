# Post-retention PPI update

This ranking update applies the retention lists supplied in the 10 screenshots on November 18, 2026. It removes all players retained by any IPL team, including players already retained by Rajasthan Royals, because those players are unavailable for Rajasthan Royals to buy at auction. It also removes Pakistan players because they are unavailable for IPL selection.

The subsequent manual update additionally removes Patrick Cummins and Nitish Reddy as SRH-retained, Andre Russell as not playing in the IPL, and the requested bowling/bowling-all-rounder profiles from the batter list: Ish Sodhi, Patrick Cummins, Maheesh Theekshana, Alzarri Joseph, and Chamika Karunaratne.
Matthew Wade is also excluded because he is unlikely to play in the next IPL cycle.

This is a post-retention availability filter, not a recalculation of player performance. The same PPI formula is used. To preserve an exact top-10 output after the availability and role exclusions, the candidate pool uses at least 100 overall balls and at least 12 pressure balls across at least 2 pressure matches; lower-exposure replacements are marked with lower confidence.

- Retained-player rows transcribed: 186
- Expanded batting candidate pool before filter: 46; removed: 31; available: 15
- Expanded bowling candidate pool before filter: 84; removed: 47; available: 37
- Final output size: top 10 batters and top 10 bowlers.

## Outputs

- `retained_players.csv`: transcribed retention list with team ownership.
- `removed_retained_ppi_players.csv`: PPI-eligible players removed by the retention filter.
- `post_retention_top10_batting_ppi.csv`: updated available batting list.
- `post_retention_top10_bowling_ppi.csv`: updated available bowling list.

The original pre-retention rankings remain unchanged in `outputs/day6/`. The new files are explicitly labelled post-retention.
