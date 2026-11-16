# sreeyans_SupeRR

Working repository for SupeRR Selector Season 2 Round 1.

The ball-by-ball source was updated on November 16, 2026. The revised `extras1_runs` field contains numeric extras amounts, so the project now reconstructs delivery totals as `runs + extras1_runs`. See [`docs/data_update_2026-11-16.md`](docs/data_update_2026-11-16.md) for the comparison and migration note.

## Day 1 automation

The Day 1 workflow inventories the supplied CSV files and creates a joined match-context table by linking `matches.csv` to `competitions.csv` on `comp_id`.

Raw competition data is intentionally excluded from Git through `.gitignore`. Place the extracted data pack under `data/raw/` locally, or provide another input directory when running the script.

```bash
python scripts/day1_inventory.py \
  --input-dir data/raw \
  --output-dir outputs/day1
```

Outputs:

- `file_inventory.csv`: file names, row counts, column counts, and schemas.
- `match_context.csv`: matches joined with competition, format, season, and stage metadata.
- `data_dictionary.md`: observed columns, types, and missing-value counts.
- `day1_summary.md`: concise findings for the project log.

## Day 2 automation

The Day 2 workflow inspects delivery-field semantics and validates a complete sample match without uploading raw data:

```bash
python scripts/day2_delivery_validation.py \
  --input-dir data/raw \
  --output-dir outputs/day2
```

It produces a delivery-semantics summary, sample-match validation table, and notes. The revised export provides numeric extra amounts in `extras1_runs`, including 1–5 for wides, byes, and leg-byes. The score rule is now `total_runs = runs + extras1_runs`; `extras_type` remains the category label and `extras_2_runs` is ignored.

## Day 3 automation

The Day 3 workflow builds delivery-level match state for all available deliveries:

```bash
python scripts/day3_match_state.py \
  --input-dir data/raw \
  --output-dir outputs/day3
```

It creates `score_before`, `wickets_before`, legal-ball state, target, runs required, required run rate, current run rate, projected final score, innings phase, and competition/stage context. It uses the corrected numeric extras rule. The repository commits a sample delivery-state table and compact all-match summary; the script can also write the full derived state locally with `--write-full`.

## Day 4 automation

The Day 4 workflow converts pre-delivery match state into pressure features and labels:

```bash
python scripts/day4_pressure_labels.py \
  --input-dir data/raw \
  --output-dir outputs/day4
```

It creates ordinary, practical-pressure, and desperation-pressure labels, first- and second-innings pressure scores, manual examples, and threshold sensitivity results. The score uses normalized required-rate, ball-resource, and wicket-resource components plus modest stage points; no delivery outcome or player performance is used.

## Current data scope

The supplied pack contains IPL/T20 data and T20I data from 2022 onward. The main analysis should distinguish:

- IPL competitions (`comp_name` contains `IPL`)
- T20I competitions (`match_format == T20I`)
- Other T20 competitions, which should be separately labelled or excluded from the primary rankings

## Project structure

```text
.
├── data/raw/          # local-only source data; not committed
├── data/processed/    # derived data; review before committing
├── outputs/day1/      # Day 1 inventory and match-context outputs
├── scripts/           # repeatable analysis scripts
├── notebooks/         # optional exploratory notebooks
└── report/            # methodology report and final submission
```

## Reproducibility

The script uses `pandas` and validates the expected many-to-one relationship between competitions and matches. It fails loudly if the join would duplicate match rows or leave competition metadata unmatched.
