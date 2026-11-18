# Post-retention PPI update

This ranking update applies the retention lists supplied in the 10 screenshots on November 18, 2026. It removes all players retained by any IPL team, including players already retained by Rajasthan Royals, because those players are unavailable for Rajasthan Royals to buy at auction. It also removes Pakistan players because they are unavailable for IPL selection.

The subsequent manual update additionally removes Patrick Cummins and Nitish Reddy as SRH-retained, Andre Russell as not playing in the IPL, and the requested bowling/bowling-all-rounder profiles from the batter list: Ish Sodhi, Patrick Cummins, Maheesh Theekshana, Alzarri Joseph, and Chamika Karunaratne.

This is a post-retention availability filter, not a recalculation of player performance. PPI values remain unchanged; only unavailable players are removed and the remaining players are re-ranked.

- Retained-player rows transcribed: 186
- Batting PPI players before filter: 17; removed: 14; available after retention: 3
- Bowling PPI players before filter: 45; removed: 30; available after retention/eligibility filter: 15

## Outputs

- `retained_players.csv`: transcribed retention list with team ownership.
- `removed_retained_ppi_players.csv`: PPI-eligible players removed by the retention filter.
- `post_retention_top10_batting_ppi.csv`: updated available batting list.
- `post_retention_top10_bowling_ppi.csv`: updated available bowling list.

The original pre-retention rankings remain unchanged in `outputs/day6/`. The new files are explicitly labelled post-retention.
