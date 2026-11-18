# Post-retention PPI update

This ranking update applies the retention lists supplied in the 10 screenshots on November 18, 2026. It removes all players retained by any IPL team, including players already retained by Rajasthan Royals, because those players are unavailable for Rajasthan Royals to buy at auction. It also removes Pakistan players because they are unavailable for IPL selection.

The subsequent manual update additionally removes Patrick Cummins and Nitish Reddy as SRH-retained, Andre Russell as not playing in the IPL, and the requested bowling/bowling-all-rounder profiles from the batter list: Ish Sodhi, Patrick Cummins, Maheesh Theekshana, Alzarri Joseph, and Chamika Karunaratne.
Matthew Wade is also excluded because he is unlikely to play in the next IPL cycle.
Mahendra Singh Dhoni is excluded as a CSK mentor, and Rasikh Salam is excluded as retained by Royal Challengers Bengaluru.

The same PPI formula is used. To preserve an exact top-10 output after all exclusions, the candidate pool uses at least 100 overall balls and at least 5 pressure balls across at least 1 pressure match. Each panel allows at most one player per non-India country and at most three Indian players; lower-exposure replacements are marked with lower confidence.

- Retained-player rows transcribed: 186
- Expanded batting candidate pool before filter: 83; removed: 47; available: 10
- Expanded bowling candidate pool before filter: 160; removed: 71; available: 10
- Final output size: top 10 batters and top 10 bowlers.

## Outputs

- `retained_players.csv`: transcribed retention list with team ownership.
- `removed_retained_ppi_players.csv`: PPI-eligible players removed by the retention filter.
- `post_retention_top10_batting_ppi.csv`: updated available batting list.
- `post_retention_top10_bowling_ppi.csv`: updated available bowling list.

The original pre-retention rankings remain unchanged in `outputs/day6/`. The new files are explicitly labelled post-retention.
