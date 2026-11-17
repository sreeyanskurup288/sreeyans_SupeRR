# Final Validation and Submission Checklist

## Pipeline status

- Updated ball-by-ball source is used.
- Delivery totals use `total_runs = runs + extras1_runs`.
- `extras_type` is retained as a category label and `extras_2_runs` is ignored.
- Raw ZIP and CSV files are excluded from the repository.
- Day 5 metrics and Day 6 PPI rankings were regenerated before this validation.

## Ranking checks

| category   |   eligible_count |   top10_count |   unique_top10_names |   duplicate_names_in_top10 |   rank_1_count |   min_pressure_sample_top10 |   max_pressure_sample_top10 |   low_confidence_top10 |
|:-----------|-----------------:|--------------:|---------------------:|---------------------------:|---------------:|----------------------------:|----------------------------:|-----------------------:|
| batting    |               17 |            10 |                   10 |                          0 |              1 |                          20 |                          41 |                      4 |
| bowling    |               45 |            10 |                   10 |                          0 |              1 |                          20 |                          38 |                      6 |

## Eligibility sensitivity

| version   |   min_pressure_balls |   min_pressure_matches |   eligible_batters |   eligible_bowlers |
|:----------|---------------------:|-----------------------:|-------------------:|-------------------:|
| main      |                   20 |                      3 |                 17 |                 45 |
| broad     |                   15 |                      3 |                 17 |                 45 |
| strict    |                   25 |                       4 |                  9 |                 30 |

## One-match dominance

The top-10 lists were checked against pressure-event concentration by match. The highest concentration is Matthew Wade at 65.2% of pressure events from one match, followed by Rovman Powell at 52.2% and Patrick Cummins at 48.7%. Bowling concentration is lower; the maximum is Harshit Rana at 37.5%. These players should receive manual review before final submission, especially where confidence is Low.

See `one_match_dominance.csv` for the complete top-10 check.

The visual ranking summary is in `top10_ppi_chart.png`.

## Preliminary top 10 batting list

|   rank | striker_name         |   PPI |   pressure_balls |   pressure_matches | confidence   |
|-------:|:---------------------|------:|-----------------:|-------------------:|:-------------|
|      1 | Matthew Wade         | 81.93 |               22 |                  4 | Low          |
|      2 | Jason Holder         | 78.08 |               27 |                  7 | Medium       |
|      3 | Towhid Hridoy        | 75.48 |               33 |                  3 | Medium       |
|      4 | Rovman Powell        | 75.44 |               20 |                  4 | Low          |
|      5 | Patrick Cummins      | 64.42 |               39 |                  5 | Medium       |
|      6 | Haris Rauf           | 61.7  |               41 |                 14 | High         |
|      7 | Noor Ahmad           | 61.19 |               21 |                  8 | Low          |
|      8 | Wellington Masakadza | 58.98 |               26 |                  7 | Medium       |
|      9 | Bhuvneshwar Kumar    | 51.34 |               23 |                  9 | Low          |
|     10 | Ish Sodhi            | 51.24 |               32 |                  8 | Medium       |

## Preliminary top 10 bowling list

|   rank | bowler_name        |   PPI |   pressure_legal_balls |   pressure_matches | confidence   |
|-------:|:-------------------|------:|-----------------------:|-------------------:|:-------------|
|      1 | Kuldeep Yadav      | 88.26 |                     20 |                  5 | Low          |
|      2 | Jasprit Bumrah     | 81.97 |                     31 |                  8 | Medium       |
|      3 | Harshit Rana       | 78.83 |                     30 |                  5 | Medium       |
|      4 | Yash Dayal         | 74.22 |                     27 |                  7 | Low          |
|      5 | Naveen ul Haq      | 73.18 |                     38 |                  7 | Medium       |
|      6 | Mohit Sharma       | 69.4  |                     27 |                  8 | Low          |
|      7 | Kyle Jamieson      | 68.71 |                     20 |                  7 | Low          |
|      8 | Maheesh Theekshana | 68.67 |                     21 |                  7 | Low          |
|      9 | Jofra Archer       | 68.43 |                     22 |                  5 | Low          |
|     10 | Abrar Ahmed        | 67.24 |                     35 |                  7 | Medium       |

## Methodology draft

This prototype defines pressure from the match state before each delivery. Practical pressure combines required-rate, ball-resource, wicket-resource, and match-stage context. Desperation is a high practical-pressure state with severely constrained remaining resources. Batting PPI combines pressure batting performance, retention versus normal deliveries, match consistency, pressure context, and reliability. Bowling PPI combines pressure economy, dot-ball rate, wicket rate, boundary suppression, retention versus normal deliveries, consistency, pressure context, and reliability.

The rankings are comparative, not definitive player-quality ratings. Small pressure samples are penalized through eligibility rules and reliability scoring. The updated extras field materially improves score reconstruction, but the analysis still depends on the supplied data's delivery classifications and the chosen pressure thresholds.

## Submission checklist

- [ ] Confirm the competition's required player-name format.
- [ ] Copy exactly 10 batters from `top10_batting_ppi.csv`.
- [ ] Copy exactly 10 bowlers from `top10_bowling_ppi.csv`.
- [ ] Confirm player names against the submission dropdown.
- [ ] Review low-confidence finalists and decide whether eligibility should be stricter.
- [ ] Review players with high one-match pressure concentration, especially Matthew Wade, Rovman Powell, and Patrick Cummins.
- [ ] Explain the pressure thresholds and corrected extras rule in the final submission.
- [ ] Upload the final report before the deadline, leaving a safety buffer.
