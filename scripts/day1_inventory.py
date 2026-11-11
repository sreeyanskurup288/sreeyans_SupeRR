#!/usr/bin/env python3
"""Inventory the SupeRR data pack and build match-level context."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd

REQUIRED_FILES = [
    "ball_by_ball.csv",
    "matches.csv",
    "competitions.csv",
    "playing_eleven.csv",
    "competition_team_player_mapping.csv",
    "teams.csv",
]


def csv_files(input_dir: Path) -> Iterable[Path]:
    return sorted(input_dir.glob("*.csv"))


def inventory(input_dir: Path) -> tuple[pd.DataFrame, str]:
    rows = []
    dictionary_sections = []
    for path in csv_files(input_dir):
        df = pd.read_csv(path)
        rows.append(
            {
                "file": path.name,
                "rows": len(df),
                "columns": len(df.columns),
                "size_bytes": path.stat().st_size,
                "columns_list": " | ".join(df.columns),
            }
        )
        dictionary_sections.append(f"## `{path.name}`\n")
        dictionary_sections.append(
            "| Column | Type | Missing | Unique |\n|---|---|---:|---:|\n"
        )
        for col in df.columns:
            dictionary_sections.append(
                f"| `{col}` | `{df[col].dtype}` | {int(df[col].isna().sum())} | "
                f"{int(df[col].nunique(dropna=True))} |\n"
            )
        dictionary_sections.append("\n")
    return pd.DataFrame(rows), "\n".join(dictionary_sections)


def build_match_context(input_dir: Path) -> pd.DataFrame:
    matches = pd.read_csv(input_dir / "matches.csv")
    competitions = pd.read_csv(input_dir / "competitions.csv")
    if competitions["comp_id"].duplicated().any():
        duplicate_ids = competitions.loc[
            competitions["comp_id"].duplicated(keep=False), "comp_id"
        ].unique().tolist()
        raise ValueError(f"Duplicate competition IDs would duplicate matches: {duplicate_ids}")

    context = matches.merge(
        competitions,
        on="comp_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    unmatched = int((context["_merge"] != "both").sum())
    if unmatched:
        raise ValueError(f"{unmatched} matches have no matching competition metadata")
    context = context.drop(columns=["_merge"])
    context["analysis_group"] = "Other T20"
    context.loc[context["match_format"].eq("T20I"), "analysis_group"] = "T20I"
    context.loc[
        context["comp_name"].str.contains("IPL", case=False, na=False),
        "analysis_group",
    ] = "IPL"
    context["stage_group"] = "Other"
    context.loc[context["stage"].eq("League"), "stage_group"] = "League"
    context.loc[context["knock_out"].eq(1), "stage_group"] = "Knockout"
    context.loc[context["stage"].eq("Final"), "stage_group"] = "Final"
    return context


def write_summary(output_dir: Path, inventory_df: pd.DataFrame, context: pd.DataFrame) -> None:
    counts = context.groupby(["analysis_group", "stage_group"]).size().reset_index(name="matches")
    lines = [
        "# Day 1 Summary",
        "",
        f"- CSV files inventoried: {len(inventory_df)}",
        f"- Matches in joined context table: {len(context)}",
        f"- Delivery rows in source pack: {int(inventory_df.loc[inventory_df.file.eq('ball_by_ball.csv'), 'rows'].iloc[0]) if (inventory_df.file == 'ball_by_ball.csv').any() else 'not found'}",
        "",
        "## Matches by analysis group and stage",
        "",
        counts.to_markdown(index=False),
        "",
        "## Notes",
        "",
        "- `analysis_group` separates IPL, T20I, and other T20 competitions.",
        "- `stage_group` uses the supplied `stage` and `knock_out` fields.",
        "- Delivery-level score and legal-ball reconstruction is intentionally deferred to a later step.",
    ]
    (output_dir / "day1_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    missing = [name for name in REQUIRED_FILES if not (args.input_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing expected files: {missing}")

    inventory_df, dictionary = inventory(args.input_dir)
    context = build_match_context(args.input_dir)
    inventory_df.to_csv(args.output_dir / "file_inventory.csv", index=False)
    context.to_csv(args.output_dir / "match_context.csv", index=False)
    (args.output_dir / "data_dictionary.md").write_text(dictionary, encoding="utf-8")
    write_summary(args.output_dir, inventory_df, context)
    print(f"Inventoried {len(inventory_df)} CSV files and {len(context)} matches.")


if __name__ == "__main__":
    main()
