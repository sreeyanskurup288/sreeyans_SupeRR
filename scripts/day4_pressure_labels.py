#!/usr/bin/env python3
"""Create match-state pressure features and labels for the SupeRR prototype."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from day3_match_state import attach_context, build_state  # noqa: E402

STAGE_PRESSURE = {"League": 0.0, "Knockout": 10.0, "Final": 15.0, "Other": 3.0}


def add_pressure_features(state: pd.DataFrame, practical_threshold: float = 75.0, desperation_threshold: float = 90.0) -> pd.DataFrame:
    out = state.copy()
    out["stage_pressure"] = out["stage_group"].map(STAGE_PRESSURE).fillna(0.03)
    out["ball_pressure"] = (
        1 - out["legal_balls_remaining"] / out["innings_balls_available"].replace(0, np.nan)
    ).clip(0, 1).fillna(0)
    out["wicket_pressure"] = (out["wickets_before"] / 10).clip(0, 1)

    chase = out["innings"].eq(2) & out["runs_required"].gt(0)
    positive_rrr = out["required_run_rate"].where(chase & out["required_run_rate"].ge(0))
    # Percentile within match format and innings phase, preventing format/phase scale effects.
    rrr_group = [out["match_format"], out["innings_phase"]]
    out["rrr_pressure"] = positive_rrr.groupby(rrr_group, observed=False).rank(pct=True).fillna(0)
    out["second_innings_pressure_score"] = (
        40 * out["rrr_pressure"]
        + 25 * out["ball_pressure"]
        + 20 * out["wicket_pressure"]
        + out["stage_pressure"]
    ).round(4)
    out["is_practical_pressure"] = chase & out["second_innings_pressure_score"].ge(practical_threshold)
    out["is_desperation_pressure"] = (
        out["is_practical_pressure"]
        & out["second_innings_pressure_score"].ge(desperation_threshold)
        & (out["legal_balls_remaining"].le(18) | out["wickets_before"].ge(7))
    )

    # First-innings exploratory pressure: compare projected score with peer scoring environment.
    first = out["innings"].eq(1)
    final_scores = out.loc[first].groupby(["match_id", "innings"], as_index=False)["total_runs_provisional"].sum()
    final_scores = final_scores.rename(columns={"total_runs_provisional": "first_innings_final_provisional"})
    out = out.merge(final_scores, on=["match_id", "innings"], how="left", validate="many_to_one")
    reference = out.loc[first].groupby(["analysis_group", "season", "innings_phase"])["first_innings_final_provisional"].transform("median")
    out.loc[first, "reference_score"] = reference
    out["projected_score_deficit"] = (out["reference_score"] - out["projected_final_score"]).clip(lower=0)
    deficit_group = [out["analysis_group"], out["season"], out["innings_phase"]]
    out["projected_score_deficit_pressure"] = out["projected_score_deficit"].groupby(deficit_group, observed=False).rank(pct=True).fillna(0)
    out["first_innings_pressure_score"] = (
        35 * out["wicket_pressure"]
        + 30 * out["ball_pressure"]
        + 20 * out["projected_score_deficit_pressure"]
        + out["stage_pressure"]
    ).round(4)
    out["first_innings_practical"] = first & out["first_innings_pressure_score"].ge(practical_threshold)
    out["first_innings_desperation"] = (
        out["first_innings_practical"]
        & out["first_innings_pressure_score"].ge(desperation_threshold)
        & out["legal_balls_remaining"].le(18)
        & out["wickets_before"].ge(6)
    )

    out["pressure_score"] = np.where(
        out["innings"].eq(2), out["second_innings_pressure_score"], out["first_innings_pressure_score"]
    )
    out["is_practical_pressure"] = out["is_practical_pressure"] | out["first_innings_practical"]
    out["is_desperation_pressure"] = out["is_desperation_pressure"] | out["first_innings_desperation"]
    out["pressure_type"] = np.select(
        [out["is_desperation_pressure"], out["is_practical_pressure"]],
        ["Desperation", "Practical"],
        default="Ordinary",
    )
    return out


def summary_table(labels: pd.DataFrame) -> pd.DataFrame:
    return (
        labels.groupby(["innings", "analysis_group", "stage_group", "pressure_type"], dropna=False)
        .size().reset_index(name="deliveries")
        .sort_values(["innings", "analysis_group", "stage_group", "pressure_type"])
    )


def examples_table(labels: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "match_id", "innings", "overid", "innings_ball_num", "analysis_group", "stage_group",
        "innings_phase", "score_before", "wickets_before", "legal_balls_remaining",
        "runs_required", "required_run_rate", "pressure_score", "pressure_type",
    ]
    parts = []
    for label in ["Ordinary", "Practical", "Desperation"]:
        subset = labels[labels.pressure_type.eq(label)].sort_values("pressure_score")
        if label == "Ordinary":
            subset = subset.tail(5)
        else:
            subset = subset.head(5)
        if not subset.empty:
            parts.append(subset[cols].copy())
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=cols)


def sensitivity(labels: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for p, d in [(80, 95), (75, 90), (70, 85)]:
        chase = labels["innings"].eq(2) & labels["runs_required"].gt(0)
        practical = chase & labels["second_innings_pressure_score"].ge(p)
        desperate = practical & labels["second_innings_pressure_score"].ge(d) & (
            labels["legal_balls_remaining"].le(18) | labels["wickets_before"].ge(7)
        )
        rows.append({
            "version": f"practical_{p}_desperation_{d}",
            "practical_threshold": p,
            "desperation_threshold": d,
            "second_innings_practical_deliveries": int(practical.sum()),
            "second_innings_desperation_deliveries": int(desperate.sum()),
            "desperation_subset_of_practical": bool((desperate & ~practical).sum() == 0),
        })
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--write-full", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    ball = pd.read_csv(args.input_dir / "ball_by_ball.csv")
    context = attach_context(ball, args.input_dir)
    state = build_state(ball, context)
    labels = add_pressure_features(state)
    summary = summary_table(labels)
    examples = examples_table(labels)
    sens = sensitivity(labels)
    summary.to_csv(args.output_dir / "pressure_label_summary.csv", index=False)
    examples.to_csv(args.output_dir / "pressure_examples.csv", index=False)
    sens.to_csv(args.output_dir / "day4_sensitivity.csv", index=False)
    if args.write_full:
        labels.to_csv(args.output_dir / "pressure_labels_full.csv", index=False)

    second = labels[labels.innings.eq(2)]
    first = labels[labels.innings.eq(1)]
    notes = [
        "# Day 4 Pressure-Label Notes",
        "",
        "## Main rule",
        "",
        "Pressure is calculated from the match state before the delivery. Delivery outcomes are not used, preventing outcome leakage.",
        "",
        "## Second innings",
        "",
        "`second_innings_pressure_score` uses 40 points of required-rate pressure, 25 points of ball-resource pressure, 20 points of wicket-resource pressure, and a stage adjustment of 0 points for League, 3 for Other, 10 for Knockout, and 15 for Final. Practical pressure is a score of at least 75 with positive runs required. Desperation is a practical-pressure delivery with a score of at least 90 and either 18 or fewer legal balls remaining or at least seven wickets already lost.",
        "",
        "## First innings",
        "",
        "`first_innings_pressure_score` is exploratory because there is no target yet. It uses wickets lost, late-innings resource pressure, projected-score deficit versus the peer scoring environment, and stage pressure. First-innings desperation additionally requires 18 or fewer balls remaining and at least six wickets lost.",
        "",
        "## Uniform extras rule",
        "",
        "The revised CSV provides numeric extras in `extras1_runs`; total delivery runs are reconstructed as `runs + extras1_runs`. `extras_type` is the category label and `extras_2_runs` is ignored.",
        "",
        "## Counts",
        "",
        f"- Deliveries processed: {len(labels):,}",
        f"- Second-innings deliveries: {len(second):,}",
        f"- First-innings deliveries: {len(first):,}",
        f"- Practical-pressure deliveries (combined): {int(labels.is_practical_pressure.sum()):,}",
        f"- Desperation-pressure deliveries (combined): {int(labels.is_desperation_pressure.sum()):,}",
        "",
        "## Reproduction",
        "",
        "```bash",
        "python scripts/day4_pressure_labels.py --input-dir /path/to/data --output-dir outputs/day4",
        "```",
        "",
        "The full delivery-level labels are intentionally not committed by default; use `--write-full` for a local downstream Day 5 run.",
    ]
    (args.output_dir / "day4_notes.md").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print(f"Processed {len(labels):,} deliveries; practical={int(labels.is_practical_pressure.sum()):,}; desperation={int(labels.is_desperation_pressure.sum()):,}.")


if __name__ == "__main__":
    main()
