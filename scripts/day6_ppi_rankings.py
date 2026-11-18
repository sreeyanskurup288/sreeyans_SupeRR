#!/usr/bin/env python3
"""Calculate transparent Day 6 Batting PPI and Bowling PPI rankings."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

BAT_MIN_TOTAL = 100
BOWL_MIN_TOTAL = 100
MIN_PRESSURE_BALLS = 20
MIN_PRESSURE_MATCHES = 3


def percentile(s: pd.Series, higher_is_better: bool = True) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    result = x.rank(pct=True, method="average") * 100
    if not higher_is_better:
        result = 100 - result
    return result.fillna(result.median() if result.notna().any() else 50).clip(0, 100)


def safe_ratio(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a / b.replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)


def bat_ranking(df: pd.DataFrame, min_pressure_balls: int = MIN_PRESSURE_BALLS, min_pressure_matches: int = MIN_PRESSURE_MATCHES) -> pd.DataFrame:
    x = df.copy()
    x = x[(x.overall_balls >= BAT_MIN_TOTAL) & (x.pressure_balls >= min_pressure_balls) & (x.pressure_matches >= min_pressure_matches)].copy()
    x["pressure_absolute_score"] = (
        0.50 * percentile(x.pressure_strike_rate)
        + 0.25 * percentile(x.pressure_dot_ball_rate, higher_is_better=False)
        + 0.25 * percentile(x.pressure_dismissal_rate, higher_is_better=False)
    )
    x["pressure_sr_retention"] = safe_ratio(x.pressure_strike_rate, x.normal_strike_rate)
    x["retention_score"] = percentile(x.pressure_sr_retention)
    x["consistency_raw"] = 1 / (1 + safe_ratio(x.pressure_match_sr_std, x.pressure_strike_rate).fillna(1))
    x["consistency_score"] = percentile(x.consistency_raw)
    x["context_score"] = percentile(x.pressure_pressure_score_mean)
    x["reliability_score"] = (100 * np.minimum(1, np.sqrt(x.pressure_balls / 50))).clip(0, 100)
    x["PPI"] = (
        0.40 * x.pressure_absolute_score
        + 0.25 * x.retention_score
        + 0.15 * x.consistency_score
        + 0.10 * x.context_score
        + 0.10 * x.reliability_score
    ).round(2)
    x["confidence"] = np.select(
        [x.pressure_balls >= 40, x.pressure_balls >= 25], ["High", "Medium"], default="Low"
    )
    x["rank"] = x.PPI.rank(method="min", ascending=False).astype(int)
    return x.sort_values(["PPI", "pressure_balls"], ascending=[False, False])


def bowl_ranking(df: pd.DataFrame, min_pressure_balls: int = MIN_PRESSURE_BALLS, min_pressure_matches: int = MIN_PRESSURE_MATCHES) -> pd.DataFrame:
    x = df.copy()
    x = x[(x.overall_legal_balls >= BOWL_MIN_TOTAL) & (x.pressure_legal_balls >= min_pressure_balls) & (x.pressure_matches >= min_pressure_matches)].copy()
    x["pressure_absolute_score"] = (
        0.35 * percentile(x.pressure_economy, higher_is_better=False)
        + 0.25 * percentile(x.pressure_dot_ball_rate)
        + 0.25 * percentile(x.pressure_wicket_rate_per_ball)
        + 0.15 * percentile(x.pressure_boundary_rate, higher_is_better=False)
    )
    x["pressure_economy_retention"] = safe_ratio(x.normal_economy, x.pressure_economy)
    x["retention_score"] = percentile(x.pressure_economy_retention)
    x["consistency_raw"] = 1 / (1 + safe_ratio(x.pressure_match_economy_std, x.pressure_economy).fillna(1))
    x["consistency_score"] = percentile(x.consistency_raw)
    x["context_score"] = percentile(x.pressure_pressure_score_mean)
    x["reliability_score"] = (100 * np.minimum(1, np.sqrt(x.pressure_legal_balls / 60))).clip(0, 100)
    x["PPI"] = (
        0.40 * x.pressure_absolute_score
        + 0.25 * x.retention_score
        + 0.15 * x.consistency_score
        + 0.10 * x.context_score
        + 0.10 * x.reliability_score
    ).round(2)
    x["confidence"] = np.select(
        [x.pressure_legal_balls >= 50, x.pressure_legal_balls >= 30], ["High", "Medium"], default="Low"
    )
    x["rank"] = x.PPI.rank(method="min", ascending=False).astype(int)
    return x.sort_values(["PPI", "pressure_legal_balls"], ascending=[False, False])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    bat = bat_ranking(pd.read_csv(args.metrics_dir / "batting_metrics.csv"))
    bowl = bowl_ranking(pd.read_csv(args.metrics_dir / "bowling_metrics.csv"))
    bat.to_csv(args.output_dir / "batting_ppi_eligible.csv", index=False)
    bowl.to_csv(args.output_dir / "bowling_ppi_eligible.csv", index=False)
    bat.head(10).to_csv(args.output_dir / "top10_batting_ppi.csv", index=False)
    bowl.head(10).to_csv(args.output_dir / "top10_bowling_ppi.csv", index=False)
    notes = [
        "# Day 6 PPI Ranking Notes",
        "",
        "## Eligibility",
        "",
        f"- Batters: at least {BAT_MIN_TOTAL} overall legal balls, {MIN_PRESSURE_BALLS} pressure balls, and {MIN_PRESSURE_MATCHES} pressure matches.",
        f"- Bowlers: at least {BOWL_MIN_TOTAL} overall legal balls, {MIN_PRESSURE_BALLS} pressure legal balls, and {MIN_PRESSURE_MATCHES} pressure matches.",
        "",
        "## Batting PPI",
        "",
        "40% pressure performance, 25% pressure strike-rate retention versus normal, 15% match consistency, 10% pressure-context score, and 10% reliability.",
        "",
        "## Bowling PPI",
        "",
        "40% pressure performance, 25% pressure economy retention versus normal, 15% match consistency, 10% pressure-context score, and 10% reliability. Lower economy and boundary rate conceded are better; higher dot-ball and wicket rates are better.",
        "",
        "## Corrected extras",
        "",
        "The rankings use the revised numeric extras field through Day 3: `total_runs = runs + extras1_runs`. The earlier one-run-per-extra approximation is no longer used.",
        "",
        f"Eligible players: {len(bat)} batters and {len(bowl)} bowlers. The top 10 files are ready for review, not final submission until sensitivity and manual player checks are complete.",
    ]
    (args.output_dir / "day6_notes.md").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print(f"Ranked {len(bat)} eligible batters and {len(bowl)} eligible bowlers.")


if __name__ == "__main__":
    main()
