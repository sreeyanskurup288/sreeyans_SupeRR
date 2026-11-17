#!/usr/bin/env python3
"""Final validation for the SupeRR Selector prototype."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def rank_with_thresholds(df: pd.DataFrame, kind: str, min_pressure: int, min_matches: int) -> pd.DataFrame:
    x = df.copy()
    if kind == "batting":
        x = x[(x.overall_balls >= 100) & (x.pressure_balls >= min_pressure) & (x.pressure_matches >= min_matches)].copy()
        x["ranking_signal"] = x.PPI
        id_col, name_col = "striker_id", "striker_name"
    else:
        x = x[(x.overall_legal_balls >= 100) & (x.pressure_legal_balls >= min_pressure) & (x.pressure_matches >= min_matches)].copy()
        x["ranking_signal"] = x.PPI
        id_col, name_col = "bowler_id", "bowler_name"
    x["rank"] = x.ranking_signal.rank(method="min", ascending=False).astype(int)
    return x[[id_col, name_col, "rank", "PPI"]].sort_values("rank")


def sensitivity_table(bat: pd.DataFrame, bowl: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, p, m in [("main", 20, 3), ("broad", 15, 3), ("strict", 25, 4)]:
        br = rank_with_thresholds(bat, "batting", p, m)
        wr = rank_with_thresholds(bowl, "bowling", p, m)
        rows.append({
            "version": label,
            "min_pressure_balls": p,
            "min_pressure_matches": m,
            "eligible_batters": len(br),
            "eligible_bowlers": len(wr),
            "top10_batters": " | ".join(br.head(10).iloc[:, 1].tolist()),
            "top10_bowlers": " | ".join(wr.head(10).iloc[:, 1].tolist()),
        })
    return pd.DataFrame(rows)


def ranking_checks(bat: pd.DataFrame, bowl: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for kind, df, name in [("batting", bat, "striker_name"), ("bowling", bowl, "bowler_name")]:
        top = df.head(10)
        rows.append({
            "category": kind,
            "eligible_count": len(df),
            "top10_count": len(top),
            "unique_top10_names": top[name].nunique(),
            "duplicate_names_in_top10": len(top) - top[name].nunique(),
            "rank_1_count": int((df["rank"] == 1).sum()),
            "min_pressure_sample_top10": int(top["pressure_balls" if kind == "batting" else "pressure_legal_balls"].min()),
            "max_pressure_sample_top10": int(top["pressure_balls" if kind == "batting" else "pressure_legal_balls"].max()),
            "low_confidence_top10": int((top["confidence"] == "Low").sum()),
        })
    return pd.DataFrame(rows)


def write_report(out: Path, bat: pd.DataFrame, bowl: pd.DataFrame, sens: pd.DataFrame, checks: pd.DataFrame) -> None:
    bat_top = bat.head(10)[["rank", "striker_name", "PPI", "pressure_balls", "pressure_matches", "confidence"]]
    bowl_top = bowl.head(10)[["rank", "bowler_name", "PPI", "pressure_legal_balls", "pressure_matches", "confidence"]]
    lines = [
        "# Final Validation and Submission Checklist",
        "",
        "## Pipeline status",
        "",
        "- Updated ball-by-ball source is used.",
        "- Delivery totals use `total_runs = runs + extras1_runs`.",
        "- `extras_type` is retained as a category label and `extras_2_runs` is ignored.",
        "- Raw ZIP and CSV files are excluded from the repository.",
        "- Day 5 metrics and Day 6 PPI rankings were regenerated before this validation.",
        "",
        "## Ranking checks",
        "",
        checks.to_markdown(index=False),
        "",
        "## Eligibility sensitivity",
        "",
        sens[["version", "min_pressure_balls", "min_pressure_matches", "eligible_batters", "eligible_bowlers"]].to_markdown(index=False),
        "",
        "## Preliminary top 10 batting list",
        "",
        bat_top.to_markdown(index=False),
        "",
        "## Preliminary top 10 bowling list",
        "",
        bowl_top.to_markdown(index=False),
        "",
        "## Methodology draft",
        "",
        "This prototype defines pressure from the match state before each delivery. Practical pressure combines required-rate, ball-resource, wicket-resource, and match-stage context. Desperation is a high practical-pressure state with severely constrained remaining resources. Batting PPI combines pressure batting performance, retention versus normal deliveries, match consistency, pressure context, and reliability. Bowling PPI combines pressure economy, dot-ball rate, wicket rate, boundary suppression, retention versus normal deliveries, consistency, pressure context, and reliability.",
        "",
        "The rankings are comparative, not definitive player-quality ratings. Small pressure samples are penalized through eligibility rules and reliability scoring. The updated extras field materially improves score reconstruction, but the analysis still depends on the supplied data's delivery classifications and the chosen pressure thresholds.",
        "",
        "## Submission checklist",
        "",
        "- [ ] Confirm the competition's required player-name format.",
        "- [ ] Copy exactly 10 batters from `top10_batting_ppi.csv`.",
        "- [ ] Copy exactly 10 bowlers from `top10_bowling_ppi.csv`.",
        "- [ ] Confirm player names against the submission dropdown.",
        "- [ ] Review low-confidence finalists and decide whether eligibility should be stricter.",
        "- [ ] Explain the pressure thresholds and corrected extras rule in the final submission.",
        "- [ ] Upload the final report before the deadline, leaving a safety buffer.",
        "",
    ]
    (out / "final_validation_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics-dir", type=Path, required=True)
    parser.add_argument("--ranking-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    bat = pd.read_csv(args.ranking_dir / "batting_ppi_eligible.csv")
    bowl = pd.read_csv(args.ranking_dir / "bowling_ppi_eligible.csv")
    sens = sensitivity_table(bat, bowl)
    checks = ranking_checks(bat, bowl)
    sens.to_csv(args.output_dir / "ranking_sensitivity.csv", index=False)
    checks.to_csv(args.output_dir / "ranking_checks.csv", index=False)
    write_report(args.output_dir, bat, bowl, sens, checks)
    print(f"Validated {len(bat)} batting and {len(bowl)} bowling eligible players.")


if __name__ == "__main__":
    main()
