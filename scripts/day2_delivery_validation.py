#!/usr/bin/env python3
"""Day 2 checks for delivery semantics and one-match validation."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

LEGAL_EXTRAS = {"wide", "Overstep"}
SAMPLE_MATCH_ID = 13511
PROVISIONAL_EXTRA_RUNS = 1


def semantic_summary(ball: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, mask in [
        ("ordinary_or_no_extra", ball["extras_type"].isna()),
        ("wide", ball["extras_type"].eq("wide")),
        ("legbyes", ball["extras_type"].eq("legbyes")),
        ("byes", ball["extras_type"].eq("byes")),
        ("overstep", ball["extras_type"].eq("Overstep")),
        ("other", ball["extras_type"].eq("other")),
        ("penalty", ball["extras_type"].eq("Penalty")),
    ]:
        subset = ball.loc[mask]
        if subset.empty:
            continue
        rows.append(
            {
                "category": label,
                "rows": len(subset),
                "runs_min": int(subset["runs"].min()),
                "runs_max": int(subset["runs"].max()),
                "extras1_values": ", ".join(map(str, sorted(subset["extras1_runs"].unique()))),
                "extras2_values": ", ".join(map(str, sorted(subset["extras_2_runs"].unique()))),
                "legal_delivery_default": label not in {"wide", "overstep"},
            }
        )
    return pd.DataFrame(rows)


def validate_match(ball: pd.DataFrame, match_id: int) -> pd.DataFrame:
    sample = ball.loc[ball["match_id"].eq(match_id)].copy()
    if sample.empty:
        raise ValueError(f"Sample match {match_id} not found")
    sample["is_legal_delivery_default"] = ~sample["extras_type"].isin(LEGAL_EXTRAS)
    sample["runs_off_bat"] = sample["runs"]
    sample["extra_event"] = sample["extras_type"].notna()
    rows = []
    for innings, group in sample.groupby("innings", sort=True):
        group = group.sort_values("innings_ball_num")
        legal = group["is_legal_delivery_default"]
        rows.append(
            {
                "match_id": match_id,
                "innings": int(innings),
                "delivery_rows": len(group),
                "first_innings_ball_num": int(group["innings_ball_num"].min()),
                "last_innings_ball_num": int(group["innings_ball_num"].max()),
                "max_overid": int(group["overid"].max()),
                "legal_deliveries": int(legal.sum()),
                "illegal_deliveries": int((~legal).sum()),
                "runs_off_bat": int(group["runs_off_bat"].sum()),
                "extra_events": int(group["extra_event"].sum()),
                "extras2_ignored_sum": int(group["extras_2_runs"].sum()),
                "wickets": int(group["is_wicket"].sum()),
                "provisional_extra_runs": int(group["extra_event"].sum() * PROVISIONAL_EXTRA_RUNS),
                "provisional_total_runs": int(
                    group["runs_off_bat"].sum() + group["extra_event"].sum() * PROVISIONAL_EXTRA_RUNS
                ),
            }
        )
    return pd.DataFrame(rows)


def write_notes(output_dir: Path, semantics: pd.DataFrame, validation: pd.DataFrame) -> None:
    lines = [
        "# Day 2 Validation Notes",
        "",
        "## Findings",
        "",
        "- `runs` is consistent with batter runs: it aligns with `is_four` and `is_six` and ranges from 0 to 6.",
        "- `extras_type` identifies wide, leg-bye, bye, overstep, other, and penalty events.",
        "- `extras1_runs` is not a usable extra-run amount: it acts like a category code (ordinary deliveries use 6; wide 2; leg-bye 3; bye 4; overstep 1; other 5; penalty 7).",
        "- `extras_2_runs` is ignored provisionally, pending a later discrepancy review.",
        "- `innings_ball_num` is unique within match and innings, but it counts delivery rows rather than legal balls.",
        "- The default legal-delivery rule for the next stage is to treat `wide` and `Overstep` as illegal, subject to further validation.",
        "",
        "## Exact-score limitation",
        "",
        "For the current prototype, every nonblank `extras_type` event is provisionally awarded one team run. This intentionally does not capture five wides or multi-run byes/leg-byes. `extras1_runs` is treated as a type ID and `extras_2_runs` is ignored. If later checks reveal a discrepancy, this rule will be revisited.",
        "",
        "## Sample match",
        "",
        "The script validates match 13511 structurally: delivery sequence, legal/illegal delivery counts, batter runs, extra events, and wickets by innings. This is a complete two-innings sample for checking the delivery-state pipeline, while the score caveat above remains applicable.",
        "",
        "## Reproduction",
        "",
        "```bash",
        "python scripts/day2_delivery_validation.py --input-dir /path/to/data --output-dir outputs/day2",
        "```",
        "",
        "## Semantic summary",
        "",
        semantics.to_markdown(index=False),
        "",
        "## Sample match validation",
        "",
        validation.to_markdown(index=False),
        "",
    ]
    (output_dir / "day2_notes.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--match-id", type=int, default=SAMPLE_MATCH_ID)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    ball = pd.read_csv(args.input_dir / "ball_by_ball.csv")
    required = {"match_id", "innings", "innings_ball_num", "overid", "runs", "is_wicket", "extras_type", "extras1_runs", "extras_2_runs"}
    missing = sorted(required.difference(ball.columns))
    if missing:
        raise ValueError(f"Missing expected ball-by-ball columns: {missing}")
    if ball.duplicated(["match_id", "innings", "innings_ball_num"]).any():
        raise ValueError("Duplicate match/innings/innings_ball_num keys found")

    semantics = semantic_summary(ball)
    validation = validate_match(ball, args.match_id)
    semantics.to_csv(args.output_dir / "delivery_semantics_summary.csv", index=False)
    validation.to_csv(args.output_dir / "sample_match_validation.csv", index=False)
    write_notes(args.output_dir, semantics, validation)
    print(f"Validated delivery semantics and match {args.match_id}.")


if __name__ == "__main__":
    main()
