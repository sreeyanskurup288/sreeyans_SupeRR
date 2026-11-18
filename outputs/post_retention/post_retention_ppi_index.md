# Post-retention PPI index

**Status: Conditional batting-runs rule applied.**

## Active filters

### Batting
- Minimum 30 innings
- Positions 1–5 (top/middle order): minimum 500 runs
- Position 6 or lower (finisher): minimum 300 runs

Each player’s role is assigned from their most frequent recorded batting position. The audit includes `typical_batting_order`, `batting_role`, and `required_runs`.

### Bowling
- Minimum 27 bowling innings
- Minimum 30 wickets
- Minimum 12 IPL/T20I innings

The batting balls-faced, strike-rate, and top-tier add-ons are removed. The bowling 660-ball/110-over minimum is also removed.

## Final result

- Available batters after all filters: **9**.
- Available bowlers after all filters: **10**.
- Tilak Varma is excluded as Mumbai Indians-retained.
- Mitchell Starc is excluded because he opted out.
- Country diversity, Pakistan, role, mentor, and all retention rules remain active.

## Available batters

| Rank | Player | Country | PPI |
|---:|---|---|---:|
| 1 | Ibrahim Zadran | Afghanistan | 76.65 |
| 2 | Towhid Hridoy | Bangladesh | 71.20 |
| 3 | Bhanuka Rajapaksa | Sri Lanka | 69.99 |
| 4 | Reeza Hendricks | South Africa | 67.95 |
| 5 | Gareth Delany | Ireland | 64.46 |
| 6 | Shikhar Dhawan | India | 56.07 |
| 7 | Ryan Burl | Zimbabwe | 42.68 |
| 8 | Deepak Hooda | India | 38.03 |
| 9 | M Shahrukh Khan | India | 21.08 |

## Available bowlers

| Rank | Player | Country | PPI |
|---:|---|---|---:|
| 1 | Mohammad Rishad Hossain | Bangladesh | 76.75 |
| 2 | Mohit Sharma | India | 72.23 |
| 3 | Naveen ul Haq | Afghanistan | 69.90 |
| 4 | Dushmantha Chameera | Sri Lanka | 65.58 |
| 5 | Tim Southee | New Zealand | 60.96 |
| 6 | Richard Ngarava | Zimbabwe | 57.70 |
| 7 | Alzarri Joseph | West Indies | 56.40 |
| 8 | Joshua Little | Ireland | 51.38 |
| 9 | Avesh Khan | India | 50.59 |
| 10 | Adil Rashid | England | 42.92 |

The batting panel has fewer than 10 eligible, available, country-compliant candidates, so it is not padded with ineligible players.

Full role-level pass/fail details are in `batting_eligibility_audit.csv`; bowling details are in `bowling_eligibility_audit.csv`.
