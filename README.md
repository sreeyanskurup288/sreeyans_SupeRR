# sreeyans_SupeRR

Working repository for SupeRR Selector Season 2 Round 1.

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

It produces a delivery-semantics summary, sample-match validation table, and notes. The current export uses `extras1_runs` as a category code rather than a numeric extras amount. For the prototype, every nonblank extra event contributes exactly one team run throughout the pipeline; `extras_2_runs` is ignored throughout. This is a uniform approximation that intentionally does not model five wides or multi-run byes/leg-byes, and can be revised consistently if later checks reveal discrepancies.

## Day 3 automation

The Day 3 workflow builds delivery-level match state for all available deliveries:

```bash
python scripts/day3_match_state.py \
  --input-dir data/raw \
  --output-dir outputs/day3
```

It creates `score_before`, `wickets_before`, legal-ball state, target, runs required, required run rate, current run rate, projected final score, innings phase, and competition/stage context. The repository commits a sample delivery-state table and compact all-match summary; the script can also write the full derived state locally with `--write-full`.

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
