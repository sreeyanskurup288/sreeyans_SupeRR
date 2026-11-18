# Day 6 — Performance Pressure Index Rankings

## Objective
Convert the Day 5 metrics into transparent batting and bowling PPI rankings.

## Tasks

1. Define the batting PPI formula from pressure performance, normal performance, and reliability.
2. Define the bowling PPI formula using the corresponding pressure and normal metrics.
3. Normalize components so no single metric dominates unintentionally.
4. Apply minimum exposure thresholds before ranking.
5. Make ranking functions reusable for post-retention replacement candidates.
6. Produce eligible pools and top-10 batting and bowling outputs.
7. Inspect whether rankings are dominated by one match or tiny samples.

## Deliverables

- `scripts/day6_ppi_rankings.py`.
- Eligible batting and bowling ranking tables under `outputs/day6/`.
- Transparent formulas and metric definitions in the README.

## Completion check

Every PPI score should be reproducible from the metric outputs, with sample-size fields visible beside the ranking.