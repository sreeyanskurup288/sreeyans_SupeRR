# Day 1 — Data Inventory and Project Setup

## Objective
Understand the supplied data pack, establish a reproducible project structure, and create the first inventory outputs.

## Tasks

1. List and inspect every CSV in the data pack.
2. Record row counts, columns, data types, missing values, and key identifiers.
3. Identify the match, competition, player, and ball-by-ball tables.
4. Check competition names, formats, seasons, and available stage metadata.
5. Create the private GitHub repository and protect raw data from accidental upload.
6. Build a repeatable inventory script that can be rerun whenever the data is updated.

## Deliverables

- Repository skeleton and README.
- `.gitignore` preventing raw ZIP and CSV uploads.
- `scripts/day1_inventory.py`.
- Inventory tables and match-context outputs under `outputs/day1/`.

## Completion check

The repository should reproduce the inventory from the local data pack with one command, without committing the raw competition files.