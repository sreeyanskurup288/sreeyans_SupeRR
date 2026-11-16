#!/usr/bin/env python3
"""Calculate Day 5 player batting and bowling metrics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from day3_match_state import attach_context, build_state  # noqa: E402
from day4_pressure_labels import add_pressure_features  # noqa: E402

BOWLER_WICKET_TYPES = {"Caught", "Bowled", "LBW", "Stump", "Hit Wicket"}
NON_BOWLER_CONCESSION_EXTRAS = {"byes", "legbyes", "Penalty"}


def load_labeled_deliveries(input_dir: Path) -> pd.DataFrame:
    ball = pd.read_csv(input_dir / "ball_by_ball.csv")
    context = attach_context(ball, input_dir)
    state = build_state(ball, context)
    labels = add_pressure_features(state)
    labels["pressure_segment"] = np.where(labels["is_practical_pressure"], "Pressure", "Normal")
    labels["batter_dismissal"] = (
        labels["is_wicket"].fillna(False)
        & (
            labels["dismissed_player_id"].eq(labels["striker_id"])
            | (labels["dismissed_player_id"].isna() & labels["dismissal_type"].eq("Retire Out"))
        )
    )
    labels["bowler_wicket"] = labels["is_wicket"].fillna(False) & labels["dismissal_type"].isin(BOWLER_WICKET_TYPES)
    labels["bowler_runs_conceded"] = labels["total_runs_provisional"] - np.where(
        labels["extras_type"].isin(NON_BOWLER_CONCESSION_EXTRAS), labels["extra_runs_provisional"], 0
    )
    labels["bowler_dot_ball"] = labels["is_legal_delivery"] & labels["total_runs_provisional"].eq(0)
    labels["boundary_event"] = labels["is_four"].fillna(False) | labels["is_six"].fillna(False)
    return labels


def _aggregate_batting(d: pd.DataFrame, player_cols: list[str], prefix: str) -> pd.DataFrame:
    g = d.groupby(player_cols, dropna=False)
    out = g.agg(
        **{
            f"{prefix}_balls": ("is_legal_delivery", "sum"),
            f"{prefix}_runs": ("runs_off_bat", "sum"),
            f"{prefix}_dismissals": ("batter_dismissal", "sum"),
            f"{prefix}_boundaries": ("boundary_event", "sum"),
            f"{prefix}_dot_balls": ("total_runs_provisional", lambda s: (s.eq(0)).sum()),
            f"{prefix}_matches": ("match_id", "nunique"),
            f"{prefix}_pressure_score_mean": ("pressure_score", "mean"),
        }
    ).reset_index()
    out[f"{prefix}_strike_rate"] = np.where(
        out[f"{prefix}_balls"] > 0, out[f"{prefix}_runs"] / out[f"{prefix}_balls"] * 100, np.nan
    )
    out[f"{prefix}_dot_ball_rate"] = np.where(
        out[f"{prefix}_balls"] > 0, out[f"{prefix}_dot_balls"] / out[f"{prefix}_balls"], np.nan
    )
    out[f"{prefix}_boundary_rate"] = np.where(
        out[f"{prefix}_balls"] > 0, out[f"{prefix}_boundaries"] / out[f"{prefix}_balls"], np.nan
    )
    out[f"{prefix}_dismissal_rate"] = np.where(
        out[f"{prefix}_balls"] > 0, out[f"{prefix}_dismissals"] / out[f"{prefix}_balls"], np.nan
    )
    return out


def _aggregate_bowling(d: pd.DataFrame, player_cols: list[str], prefix: str) -> pd.DataFrame:
    g = d.groupby(player_cols, dropna=False)
    out = g.agg(
        **{
            f"{prefix}_legal_balls": ("is_legal_delivery", "sum"),
            f"{prefix}_runs_conceded": ("bowler_runs_conceded", "sum"),
            f"{prefix}_wickets": ("bowler_wicket", "sum"),
            f"{prefix}_boundaries_conceded": ("boundary_event", "sum"),
            f"{prefix}_dot_balls": ("bowler_dot_ball", "sum"),
            f"{prefix}_matches": ("match_id", "nunique"),
            f"{prefix}_pressure_score_mean": ("pressure_score", "mean"),
        }
    ).reset_index()
    out[f"{prefix}_economy"] = np.where(
        out[f"{prefix}_legal_balls"] > 0,
        out[f"{prefix}_runs_conceded"] / out[f"{prefix}_legal_balls"] * 6,
        np.nan,
    )
    out[f"{prefix}_dot_ball_rate"] = np.where(
        out[f"{prefix}_legal_balls"] > 0, out[f"{prefix}_dot_balls"] / out[f"{prefix}_legal_balls"], np.nan
    )
    out[f"{prefix}_wicket_rate_per_ball"] = np.where(
        out[f"{prefix}_legal_balls"] > 0, out[f"{prefix}_wickets"] / out[f"{prefix}_legal_balls"], np.nan
    )
    out[f"{prefix}_boundary_rate"] = np.where(
        out[f"{prefix}_legal_balls"] > 0, out[f"{prefix}_boundaries_conceded"] / out[f"{prefix}_legal_balls"], np.nan
    )
    return out


def build_metrics(labels: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    player_cols_bat = ["striker_id", "striker_name"]
    player_cols_bowl = ["bowler_id", "bowler_name"]
    bat = _aggregate_batting(labels, player_cols_bat, "overall")
    bat = bat.merge(_aggregate_batting(labels[labels.pressure_segment.eq("Normal")], player_cols_bat, "normal"), on=player_cols_bat, how="left")
    bat = bat.merge(_aggregate_batting(labels[labels.pressure_segment.eq("Pressure")], player_cols_bat, "pressure"), on=player_cols_bat, how="left")
    bowl = _aggregate_bowling(labels, player_cols_bowl, "overall")
    bowl = bowl.merge(_aggregate_bowling(labels[labels.pressure_segment.eq("Normal")], player_cols_bowl, "normal"), on=player_cols_bowl, how="left")
    bowl = bowl.merge(_aggregate_bowling(labels[labels.pressure_segment.eq("Pressure")], player_cols_bowl, "pressure"), on=player_cols_bowl, how="left")

    # Match-level pressure variability supports a transparent consistency score in Day 6.
    bat_match = labels[labels.pressure_segment.eq("Pressure")].groupby(["striker_id", "match_id"]).agg(
        pressure_balls=("is_legal_delivery", "sum"), pressure_runs=("runs_off_bat", "sum")
    ).reset_index()
    bat_match["pressure_sr"] = np.where(bat_match.pressure_balls.gt(0), bat_match.pressure_runs / bat_match.pressure_balls * 100, np.nan)
    bat_consistency = bat_match[bat_match.pressure_balls.ge(5)].groupby("striker_id").pressure_sr.agg(pressure_match_sr_std="std", pressure_match_count="count").reset_index()
    bat = bat.merge(bat_consistency, on="striker_id", how="left")

    bowl_match = labels[labels.pressure_segment.eq("Pressure")].groupby(["bowler_id", "match_id"]).agg(
        pressure_balls=("is_legal_delivery", "sum"), pressure_runs=("bowler_runs_conceded", "sum")
    ).reset_index()
    bowl_match["pressure_economy"] = np.where(bowl_match.pressure_balls.gt(0), bowl_match.pressure_runs / bowl_match.pressure_balls * 6, np.nan)
    bowl_consistency = bowl_match[bowl_match.pressure_balls.ge(6)].groupby("bowler_id").pressure_economy.agg(pressure_match_economy_std="std", pressure_match_count="count").reset_index()
    bowl = bowl.merge(bowl_consistency, on="bowler_id", how="left")
    return bat, bowl, labels


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--write-full-labels", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    labels = load_labeled_deliveries(args.input_dir)
    batting, bowling, labels = build_metrics(labels)
    batting.to_csv(args.output_dir / "batting_metrics.csv", index=False)
    bowling.to_csv(args.output_dir / "bowling_metrics.csv", index=False)
    if args.write_full_labels:
        labels.to_csv(args.output_dir / "pressure_labels_for_metrics.csv", index=False)
    notes = [
        "# Day 5 Player Metrics",
        "",
        "## Pressure sample",
        "",
        "A delivery is in the pressure segment when the Day 4 `is_practical_pressure` flag is true; all other deliveries form the normal baseline. Batting uses legal deliveries for balls faced and runs off the bat for scoring. Bowling uses legal deliveries, excludes byes/leg-byes/penalty from bowler runs conceded, and credits wickets only for bowler-attributable dismissal types.",
        "",
        "## Corrected extras",
        "",
        "The updated ball-by-ball CSV provides numeric extras in `extras1_runs`. Day 5 uses `total_runs = runs + extras1_runs` through the Day 3 state builder.",
        "",
        "## Outputs",
        "",
        "- `batting_metrics.csv`: overall, normal, and pressure batting metrics.",
        "- `bowling_metrics.csv`: overall, normal, and pressure bowling metrics.",
        "- Use `--write-full-labels` only for a local downstream run; raw data and full delivery labels are not committed by default.",
    ]
    (args.output_dir / "day5_notes.md").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print(f"Calculated metrics for {len(batting)} batters and {len(bowling)} bowlers.")


if __name__ == "__main__":
    main()
