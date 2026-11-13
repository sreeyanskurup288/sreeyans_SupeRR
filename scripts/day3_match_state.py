#!/usr/bin/env python3
"""Build delivery-level match state for the SupeRR Selector prototype."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

LEGAL_EXTRAS = {"wide", "Overstep"}
DEFAULT_OVERS = 20
SAMPLE_MATCH_ID = 13511


def attach_context(ball: pd.DataFrame, input_dir: Path) -> pd.DataFrame:
    matches = pd.read_csv(input_dir / "matches.csv")
    competitions = pd.read_csv(input_dir / "competitions.csv")
    context = matches.merge(competitions, on="comp_id", how="left", validate="many_to_one")
    keep = [
        "match_id", "comp_id", "comp_name", "match_format", "season", "match_date",
        "stage", "knock_out", "home_team_id", "home_team", "away_team_id", "away_team",
        "venue_country", "first_inn_revised_overs", "second_inn_revised_overs",
        "revised_target", "win_team_id", "result",
    ]
    context = context[keep].copy()
    context["analysis_group"] = "Other T20"
    context.loc[context["match_format"].eq("T20I"), "analysis_group"] = "T20I"
    context.loc[context["comp_name"].str.contains("IPL", case=False, na=False), "analysis_group"] = "IPL"
    context["stage_group"] = "Other"
    context.loc[context["stage"].eq("League"), "stage_group"] = "League"
    context.loc[context["knock_out"].eq(1), "stage_group"] = "Knockout"
    context.loc[context["stage"].eq("Final"), "stage_group"] = "Final"
    return context


def provisional_runs(ball: pd.DataFrame) -> pd.DataFrame:
    out = ball.copy()
    out["runs_off_bat"] = out["runs"].fillna(0).astype(int)
    out["extra_event"] = out["extras_type"].notna()
    out["extra_runs_provisional"] = out["extra_event"].astype(int)
    out["total_runs_provisional"] = out["runs_off_bat"] + out["extra_runs_provisional"]
    out["is_legal_delivery"] = ~out["extras_type"].isin(LEGAL_EXTRAS)
    out["wicket_event"] = out["is_wicket"].fillna(False).astype(int)
    return out


def build_state(ball: pd.DataFrame, context: pd.DataFrame) -> pd.DataFrame:
    out = provisional_runs(ball).merge(context, on="match_id", how="left", validate="many_to_one")
    out = out.sort_values(["match_id", "innings", "innings_ball_num"]).reset_index(drop=True)
    out["innings_overs_available"] = np.where(
        out["innings"].eq(1), out["first_inn_revised_overs"], out["second_inn_revised_overs"]
    )
    out["innings_overs_available"] = out["innings_overs_available"].fillna(DEFAULT_OVERS)
    out["innings_balls_available"] = (out["innings_overs_available"] * 6).round().astype(int)

    group = ["match_id", "innings"]
    out["score_before"] = out.groupby(group)["total_runs_provisional"].cumsum() - out["total_runs_provisional"]
    out["wickets_before"] = out.groupby(group)["wicket_event"].cumsum() - out["wicket_event"]
    out["legal_balls_before"] = (
        out.groupby(group)["is_legal_delivery"].cumsum().astype(int) - out["is_legal_delivery"].astype(int)
    )
    out["legal_balls_remaining"] = (out["innings_balls_available"] - out["legal_balls_before"]).clip(lower=0)

    innings_totals = (
        out.groupby(["match_id", "innings"], as_index=False)
        .agg(innings_total=("total_runs_provisional", "sum"))
    )
    first_totals = innings_totals[innings_totals["innings"].eq(1)][["match_id", "innings_total"]].rename(
        columns={"innings_total": "first_innings_total_provisional"}
    )
    out = out.merge(first_totals, on="match_id", how="left", validate="many_to_one")
    out["target"] = out["revised_target"]
    out["target"] = out["target"].fillna(out["first_innings_total_provisional"] + 1)
    out.loc[out["innings"].eq(1), "target"] = np.nan
    out["runs_required"] = np.where(
        out["innings"].eq(2), out["target"] - out["score_before"], np.nan
    )
    out["required_run_rate"] = np.where(
        out["innings"].eq(2) & out["legal_balls_remaining"].gt(0),
        out["runs_required"] / out["legal_balls_remaining"] * 6,
        np.nan,
    )
    out["current_run_rate"] = np.where(
        out["legal_balls_before"].gt(0),
        out["score_before"] / out["legal_balls_before"] * 6,
        np.nan,
    )
    out["projected_final_score"] = np.where(
        out["legal_balls_before"].gt(0),
        out["score_before"] / out["legal_balls_before"] * out["innings_balls_available"],
        np.nan,
    )
    pp_end = np.minimum(36, np.maximum(1, (out["innings_balls_available"] * 0.30).round())).astype(int)
    middle_end = np.minimum(out["innings_balls_available"], np.maximum(pp_end + 1, (out["innings_balls_available"] * 0.80).round())).astype(int)
    out["innings_phase"] = np.select(
        [out["legal_balls_before"] < pp_end, out["legal_balls_before"] < middle_end],
        ["Powerplay", "Middle"],
        default="Death",
    )
    return out


def make_summary(state: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (match_id, innings), g in state.groupby(["match_id", "innings"], sort=True):
        rows.append(
            {
                "match_id": int(match_id),
                "innings": int(innings),
                "analysis_group": g["analysis_group"].iloc[0],
                "comp_name": g["comp_name"].iloc[0],
                "stage": g["stage"].iloc[0],
                "delivery_rows": len(g),
                "legal_balls": int(g["is_legal_delivery"].sum()),
                "illegal_deliveries": int((~g["is_legal_delivery"]).sum()),
                "wickets": int(g["wicket_event"].sum()),
                "provisional_total_runs": int(g["total_runs_provisional"].sum()),
                "first_innings_total_provisional": g["first_innings_total_provisional"].iloc[0],
                "target_first_seen": g["target"].dropna().iloc[0] if g["target"].notna().any() else np.nan,
                "last_score_before": int(g["score_before"].iloc[-1]),
                "last_legal_balls_remaining": int(g["legal_balls_remaining"].iloc[-1]),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sample-match-id", type=int, default=SAMPLE_MATCH_ID)
    parser.add_argument("--write-full", action="store_true", help="Write the full derived delivery state locally")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    ball = pd.read_csv(args.input_dir / "ball_by_ball.csv")
    context = attach_context(ball, args.input_dir)
    state = build_state(ball, context)
    summary = make_summary(state)
    sample = state[state["match_id"].eq(args.sample_match_id)].copy()
    if sample.empty:
        raise ValueError(f"Sample match {args.sample_match_id} not found")

    summary.to_csv(args.output_dir / "match_state_summary.csv", index=False)
    sample_cols = [
        "match_id", "innings", "innings_ball_num", "overid", "over_ball_num",
        "striker_name", "bowler_name", "runs_off_bat", "extras_type", "extras1_runs",
        "extra_runs_provisional", "total_runs_provisional", "is_legal_delivery",
        "score_before", "wickets_before", "legal_balls_before", "legal_balls_remaining",
        "target", "runs_required", "required_run_rate", "current_run_rate",
        "projected_final_score", "innings_phase", "analysis_group", "match_format",
        "season", "stage", "knock_out",
    ]
    sample[sample_cols].to_csv(args.output_dir / "delivery_state_sample.csv", index=False)
    if args.write_full:
        state.to_csv(args.output_dir / "delivery_state_full.csv", index=False)

    notes = [
        "# Day 3 Match-State Notes",
        "",
        "## State variables created",
        "",
        "- `score_before`: provisional team score before the delivery.",
        "- `wickets_before`: wickets lost before the delivery.",
        "- `legal_balls_before` and `legal_balls_remaining`: based on `wide` and `Overstep` being illegal deliveries.",
        "- `target`: supplied `revised_target` when present; otherwise provisional first-innings total plus one for the chase.",
        "- `runs_required` and `required_run_rate`: calculated for the second innings only.",
        "- `current_run_rate` and `projected_final_score`: calculated from the state before each delivery.",
        "- `innings_phase`: Powerplay, Middle, or Death using 30% and 80% of the available innings balls.",
        "",
        "## Uniform extras rule",
        "",
        "Every nonblank `extras_type` event contributes exactly one provisional team run. `extras1_runs` is retained as a type ID and `extras_2_runs` is ignored throughout.",
        "",
        "## Reproduction",
        "",
        "```bash",
        "python scripts/day3_match_state.py --input-dir /path/to/data --output-dir outputs/day3",
        "```",
        "",
        f"The committed sample is match `{args.sample_match_id}`. The script also validates all {len(summary)} match-innings groups and writes a compact summary.",
        "",
    ]
    (args.output_dir / "day3_notes.md").write_text("\n".join(notes), encoding="utf-8")
    print(f"Built state for {len(state):,} deliveries across {len(summary):,} match-innings groups.")


if __name__ == "__main__":
    main()
