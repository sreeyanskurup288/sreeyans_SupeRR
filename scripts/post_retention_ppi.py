#!/usr/bin/env python3
"""Filter PPI rankings after IPL retention, including Rajasthan Royals' own squad."""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd

from day6_ppi_rankings import bat_ranking, bowl_ranking

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
    "patcummins": "patrickcummins",
    "nitishreddy": "nitishkumareddy",
    "rsai kishore": "rsai kishore",
}

PAKISTAN_PLAYERS = {
    "Babar Azam",
    "Haris Rauf",
    "Abrar Ahmed",
    "Shaheen Afridi",
    "Faheem Ashraf",
    "Mohammad Nawaz",
    "Sufiyan Muqeem",
    "Mohammad Saifuddin",
    "Naseem Shah",
    "Mohammad Rizwan",
    "Shadab Khan",
    "Imad Wasim",
    "Fakhar Zaman",
    "Iftikhar Ahmed",
    "Azam Khan",
    "Saim Ayub",
    "Usama Mir",
    "Mohammad Amir",
    "Khushdil Shah",
    "Hasan Ali",
    "Mohammad Hasnain",
    "Shahnawaz Dahani",
    "Haider Ali",
}

MANUAL_BATTER_EXCLUSIONS = {
    "Ish Sodhi": "Bowler/part-time batting profile — not counted as a proper batter",
    "Maheesh Theekshana": "Bowler/part-time batting profile — not counted as a proper batter",
    "Alzarri Joseph": "Bowler profile — not counted as a proper batter",
    "Chamika Karunaratne": "Bowling all-rounder — not counted as a proper batter",
}

MANUAL_GLOBAL_EXCLUSIONS = {
    "Andre Russell": "Not playing in the IPL",
    "Matthew Wade": "Unlikely to play in the next IPL cycle",
}

MANUAL_BOWLER_EXCLUSIONS = {
    "Nitish Reddy": "Retained by Sunrisers Hyderabad",
}

POST_RETENTION_MIN_PRESSURE_BALLS = 12
POST_RETENTION_MIN_PRESSURE_MATCHES = 2


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


def filter_rankings(df: pd.DataFrame, name_col: str, retention: pd.DataFrame, category: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    retained = retention.groupby("name_key", as_index=True).agg(
        team=("team", lambda s: "; ".join(sorted(set(s)))),
        rr_owned=("rr_owned", "max"),
    )
    x = df.copy()
    x["name_key"] = x[name_col].map(norm)
    x["retained_by"] = x["name_key"].map(retained["team"])
    x["retained_by_rr"] = x["name_key"].map(retained["rr_owned"]).fillna(False).astype(bool)
    x["pakistan_excluded"] = x[name_col].isin(PAKISTAN_PLAYERS)
    manual = dict(MANUAL_GLOBAL_EXCLUSIONS)
    manual.update(MANUAL_BATTER_EXCLUSIONS if category == "batting" else MANUAL_BOWLER_EXCLUSIONS)
    x["manual_exclusion_reason"] = x[name_col].map(manual).fillna("")
    x["removal_reason"] = ""
    x.loc[x.retained_by.notna(), "removal_reason"] = "Retained by IPL team"
    x.loc[x.pakistan_excluded, "removal_reason"] = "Pakistan player — unavailable for IPL selection"
    x.loc[x.manual_exclusion_reason.ne(""), "removal_reason"] = x.loc[x.manual_exclusion_reason.ne(""), "manual_exclusion_reason"]
    removed = x[x.removal_reason.ne("")].copy()
    available = x[x.removal_reason.eq("")].copy()
    available["post_retention_rank"] = range(1, len(available) + 1)
    available = available.drop(columns=["name_key"])
    return available, removed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ranking-dir", type=Path, required=True)
    parser.add_argument("--metrics-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    retention = retention_table()
    retention.to_csv(args.output_dir / "retained_players.csv", index=False)
    metrics_dir = args.metrics_dir or (args.ranking_dir.parent / "day5")
    bat_source = pd.read_csv(metrics_dir / "batting_metrics.csv")
    bowl_source = pd.read_csv(metrics_dir / "bowling_metrics.csv")
    # Keep the Day 6 minimum of 100 overall balls, but relax pressure exposure
    # only enough to fill the requested top-10 availability lists.
    bat = bat_ranking(bat_source, POST_RETENTION_MIN_PRESSURE_BALLS, POST_RETENTION_MIN_PRESSURE_MATCHES)
    bowl = bowl_ranking(bowl_source, POST_RETENTION_MIN_PRESSURE_BALLS, POST_RETENTION_MIN_PRESSURE_MATCHES)
    bat_avail, bat_removed = filter_rankings(bat, "striker_name", retention, "batting")
    bowl_avail, bowl_removed = filter_rankings(bowl, "bowler_name", retention, "bowling")
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
        "The subsequent manual update additionally removes Patrick Cummins and Nitish Reddy as SRH-retained, Andre Russell as not playing in the IPL, and the requested bowling/bowling-all-rounder profiles from the batter list: Ish Sodhi, Patrick Cummins, Maheesh Theekshana, Alzarri Joseph, and Chamika Karunaratne.",
        "Matthew Wade is also excluded because he is unlikely to play in the next IPL cycle.",
        "",
        f"This is a post-retention availability filter, not a recalculation of player performance. The same PPI formula is used. To preserve an exact top-10 output after the availability and role exclusions, the candidate pool uses at least 100 overall balls and at least {POST_RETENTION_MIN_PRESSURE_BALLS} pressure balls across at least {POST_RETENTION_MIN_PRESSURE_MATCHES} pressure matches; lower-exposure replacements are marked with lower confidence.",
        "",
        f"- Retained-player rows transcribed: {len(retention)}",
        f"- Expanded batting candidate pool before filter: {len(bat)}; removed: {len(bat_removed)}; available: {len(bat_avail)}",
        f"- Expanded bowling candidate pool before filter: {len(bowl)}; removed: {len(bowl_removed)}; available: {len(bowl_avail)}",
        f"- Final output size: top {min(10, len(bat_avail))} batters and top {min(10, len(bowl_avail))} bowlers.",
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
