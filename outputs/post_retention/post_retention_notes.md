# Post-retention PPI update

This ranking update applies the retention lists supplied in the 10 screenshots on November 18, 2026. It removes all players retained by any IPL team, including players already retained by Rajasthan Royals, because those players are unavailable for Rajasthan Royals to buy at auction. It also removes Pakistan players because they are unavailable for IPL selection.

The subsequent manual update additionally removes Patrick Cummins and Nitish Reddy as SRH-retained, Andre Russell as not playing in the IPL, and the requested bowling/bowling-all-rounder profiles from the batter list: Ish Sodhi, Patrick Cummins, Maheesh Theekshana, Alzarri Joseph, and Chamika Karunaratne.
Matthew Wade is also excluded because he is unlikely to play in the next IPL cycle.
Mahendra Singh Dhoni is excluded as a CSK mentor, Rasikh Salam is excluded as retained by Royal Challengers Bengaluru, Namboori Tilak Varma is excluded as retained by Mumbai Indians, and Mitchell Starc is excluded because he opted out.

The same PPI formula is used. Batting eligibility requires at least 25 innings plus a role-based runs minimum: positions 1–5 (top/middle order) require 500 runs, while position 6 or lower (finishers) require 300 runs. Bowling eligibility requires at least 27 innings, 30 wickets, and 12 top-tier innings; the 660-ball overs minimum has been removed. The country-diversity constraint has been removed; final panels are ranked purely by PPI after all eligibility and availability filters.

- Retained-player rows transcribed: 186
- Expanded batting candidate pool before filter: 42; removed: 29; available: 10
- Expanded bowling candidate pool before filter: 88; removed: 55; available: 10
- Final output size: 10 eligible batters and 10 eligible bowlers. The batting list is not padded when fewer than 10 players satisfy every rule.
- Eligibility audit files report every individual minimum and failed rule.

## Outputs

- `retained_players.csv`: transcribed retention list with team ownership.
- `removed_retained_ppi_players.csv`: PPI-eligible players removed by the retention filter.
- `post_retention_top10_batting_ppi.csv`: updated available batting list.
- `post_retention_top10_bowling_ppi.csv`: updated available bowling list.

The original pre-retention rankings remain unchanged in `outputs/day6/`. The new files are explicitly labelled post-retention.
