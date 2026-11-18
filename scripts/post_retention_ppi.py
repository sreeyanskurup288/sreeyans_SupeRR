#!/usr/bin/env python3
"""Filter PPI rankings after IPL retention, including Rajasthan Royals' own squad."""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd

RETENTIONS = {
    "Chennai Super Kings": """Akeal Hosein|Anshul Kamboj|Ayush Mhatre|Dewald Brevis|Gurjapneet Singh|Jack Edwards|Jamie Overton|Kartik Sharma|Liam Livingstone|Mukesh Choudhary|Noor Ahmad|Rahul Chahar|Ramakrishna Ghosh|Ruturaj Gaikwad|Sanju Samson|Sarfaraz Khan|Shivam Dube|Shreyas Gopal|Urvil Patel""",
    "Delhi Capitals": """Ashutosh Sharma|Auqib Nabi|Axar Patel|David Miller|KL Rahul|Kyle Jamieson|Lungisani Ngidi|Madhav Tiwari|Mukesh Kumar|Prithvi Shaw|Rishabh Pant|Sameer Rizvi|Tripurana Vijay|Vipraj Nigam|Zeeshan Ansari|Tristan Stubbs""",
    "Gujarat Titans": """Anuj Rawat|Ashok Sharma|Glenn Phillips|Gurjapneet Brar|Harshal Patel|Jason Holder|Jayant Yadav|Jos Buttler|Kagiso Rabada|Kumar Kushagra|Manav Suthar|Mohd. Siraj|Mohd. Arshad Khan|Nishant Sindhu|Prasidh Krishna|R. Sai Kishore|Rahul Tewatia|Rashid Khan|Sai Sudharsan|Shubman Gill|Tom Banton|Washington Sundar""",
    "Kolkata Knight Riders": """Angkrish Raghuvanshi|Anukul Roy|Cameron Green|Finn Allen|Harshit Rana|Kartik Tyagi|Manish Pandey|Prashant Solanki|Ramandeep Singh|Rinku Singh|Rovman Powell|Sarthak Ranjan|Saurabh Dubey|Sunil Narine|Tim Seifert|Vaibhav Arora|Varun Chakravarthy""",
    "Lucknow Super Giants": """Abdul Samad|Aiden Markram|Akash Singh|Akshat Raghuwanshi|Arjun Tendulkar|Arshin Kulkarni|Ayush Badoni|Digvesh Rathi|Josh Inglis|Kuldeep Yadav|Mayank Yadav|Mitchell Marsh|Mohsin Khan|Mukul Choudhary|Nicholas Pooran|Prince Yadav|Sam Curran|Shahbaz Ahmed|Yash Thakur|Xavier Bartlett""",
    "Mumbai Indians": """Arshdeep Singh|Ashwani Kumar|Corbin Bosch|Jasprit Bumrah|Mitchell Santner|Naman Dhir|Quinton de Kock|Raghu Sharma|Raj Angad Bawa|Rohit Sharma|Ryan Rickelton|Shardul Thakur|Sherfane Rutherford|Suryakumar Yadav|Tilak Varma|Will Jacks""",
    "Punjab Kings": """Azmatullah Omarzai|Ben Dwarshuis|Cooper Connolly|Hardik Pandya|Harnoor Pannu|Harpreet Brar|Marco Jansen|Marcus Stoinis|Musheer Khan|Prabhsimran Singh|Priyansh Arya|Shashank Singh|Shreyas Iyer|Suryansh Shedge|Vishnu Vinod|Vyshak Vijaykumar|Xavier Bartlett|Yash Thakur|Yuzvendra Chahal""",
    "Rajasthan Royals": """Aman Rao|Brijesh Sharma|Dasun Shanaka|Dhruv Jurel|Donovan Ferreira|Jofra Archer|Lhuan-dre Pretorius|Manimaran Siddharth|Mohd. Shami|Nandre Burger|Ravi Bishnoi|Ravindra Jadeja|Riyan Parag|Sandeep Sharma|Shubham Dubey|Sushant Mishra|Vaibhav Sooryavanshi|Yash Raj Punja|Yashasvi Jaiswal""",
    "Royal Challengers Bengaluru": """Abhinandan Singh|Bhuvneshwar Kumar|Devdutt Padikkal|Jacob Duffy|Jitesh Sharma|Jordan Cox|Josh Hazlewood|Kanishk Chouhan|Krunal Pandya|Nuwan Thushara|Phil Salt|Rajat Patidar|Rasikh Dar|Romario Shepherd|Suyash Sharma|Tim David|Venkatesh Iyer|Vicky Ostwal|Virat Kohli|Yash Dayal""",
    "Sunrisers Hyderabad": """Abhishek Sharma|Aniket Verma|Brydon Carse|Eshan Malinga|Harsh Dubey|Heinrich Klaasen|Ishan Kishan|Khaleel Ahmed|Krains Fulettra|Nathan Ellis|Nitish Kumar Reddy|Pat Cummins|Prafull Hinge|Sakib Hussain|Salil Arora|Shivang Kumar|Smaran Ravichandran|T. Natarajan""",
}

ALIASES = {
    "mohammedsiraj": "mohdsiraj",
    "mohammedshami": "mohdshami",
    "mohammedarshadkhan": "mohdarshadkhan",
    "r sai kishore": "rsai kishore",
    "rsai kishore": "rsai kishore",
}

PAKISTAN_PLAYERS = {
    "Haris Rauf",
    "Abrar Ahmed",
    "Mohammad Saifuddin",
    "Naseem Shah",
}


def norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]", "", s)
    return ALIASES.get(s, s)


def retention_table() -> pd.DataFrame:
    rows = []
    for team, raw in RETENTIONS.items():
        for player in raw.split("|"):
            rows.append({"team": team, "retained_player": player, "name_key": norm(player), "rr_owned": team == "Rajasthan Royals"})
    return pd.DataFrame(rows).drop_duplicates(["team", "name_key"])


def filter_rankings(df: pd.DataFrame, name_col: str, retention: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    retained = retention.groupby("name_key", as_index=True).agg(
        team=("team", lambda s: "; ".join(sorted(set(s)))),
        rr_owned=("rr_owned", "max"),
    )
    x = df.copy()
    x["name_key"] = x[name_col].map(norm)
    x["retained_by"] = x["name_key"].map(retained["team"])
    x["retained_by_rr"] = x["name_key"].map(retained["rr_owned"]).fillna(False).astype(bool)
    x["pakistan_excluded"] = x[name_col].isin(PAKISTAN_PLAYERS)
    x["removal_reason"] = ""
    x.loc[x.retained_by.notna(), "removal_reason"] = "Retained by IPL team"
    x.loc[x.pakistan_excluded, "removal_reason"] = "Pakistan player — unavailable for IPL selection"
    removed = x[x.removal_reason.ne("")].copy()
    available = x[x.removal_reason.eq("")].copy()
    available["post_retention_rank"] = range(1, len(available) + 1)
    available = available.drop(columns=["name_key"])
    return available, removed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ranking-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    retention = retention_table()
    retention.to_csv(args.output_dir / "retained_players.csv", index=False)
    bat = pd.read_csv(args.ranking_dir / "batting_ppi_eligible.csv")
    bowl = pd.read_csv(args.ranking_dir / "bowling_ppi_eligible.csv")
    bat_avail, bat_removed = filter_rankings(bat, "striker_name", retention)
    bowl_avail, bowl_removed = filter_rankings(bowl, "bowler_name", retention)
    bat_avail.to_csv(args.output_dir / "post_retention_batting_ppi.csv", index=False)
    bowl_avail.to_csv(args.output_dir / "post_retention_bowling_ppi.csv", index=False)
    bat_avail.head(10).to_csv(args.output_dir / "post_retention_top10_batting_ppi.csv", index=False)
    bowl_avail.head(10).to_csv(args.output_dir / "post_retention_top10_bowling_ppi.csv", index=False)
    pd.concat([
        bat_removed.assign(category="batting").rename(columns={"striker_name": "player_name"}),
        bowl_removed.assign(category="bowling").rename(columns={"bowler_name": "player_name"}),
    ], ignore_index=True).to_csv(args.output_dir / "removed_retained_ppi_players.csv", index=False)
    lines = [
        "# Post-retention PPI update",
        "",
        "This ranking update applies the retention lists supplied in the 10 screenshots on November 18, 2026. It removes all players retained by any IPL team, including players already retained by Rajasthan Royals, because those players are unavailable for Rajasthan Royals to buy at auction. It also removes Pakistan players because they are unavailable for IPL selection.",
        "",
        "This is a post-retention availability filter, not a recalculation of player performance. PPI values remain unchanged; only unavailable players are removed and the remaining players are re-ranked.",
        "",
        f"- Retained-player rows transcribed: {len(retention)}",
        f"- Batting PPI players before filter: {len(bat)}; removed: {len(bat_removed)}; available after retention: {len(bat_avail)}",
        f"- Bowling PPI players before filter: {len(bowl)}; removed: {len(bowl_removed)}; available after retention/eligibility filter: {len(bowl_avail)}",
        "",
        "## Outputs",
        "",
        "- `retained_players.csv`: transcribed retention list with team ownership.",
        "- `removed_retained_ppi_players.csv`: PPI-eligible players removed by the retention filter.",
        "- `post_retention_top10_batting_ppi.csv`: updated available batting list.",
        "- `post_retention_top10_bowling_ppi.csv`: updated available bowling list.",
        "",
        "The original pre-retention rankings remain unchanged in `outputs/day6/`. The new files are explicitly labelled post-retention.",
    ]
    (args.output_dir / "post_retention_notes.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Retention rows={len(retention)}; batting removed={len(bat_removed)}, available={len(bat_avail)}; bowling removed={len(bowl_removed)}, available={len(bowl_avail)}")


if __name__ == "__main__":
    main()
