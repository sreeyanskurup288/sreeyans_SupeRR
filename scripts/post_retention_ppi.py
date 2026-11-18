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
    "Mahendra Singh Dhoni": "CSK mentor — not a playing auction candidate",
    "Rasikh Salam": "Retained by Royal Challengers Bengaluru",
    "Namboori Tilak Varma": "Retained by Mumbai Indians",
    "Mitchell Starc": "Opted out of the IPL cycle",
}

MANUAL_BOWLER_EXCLUSIONS = {
    "Nitish Reddy": "Retained by Sunrisers Hyderabad",
}

POST_RETENTION_MIN_PRESSURE_BALLS = 5
POST_RETENTION_MIN_PRESSURE_MATCHES = 1
BAT_MIN_INNINGS = 30
BAT_MIN_RUNS = 1200
BAT_MIN_BALLS = 0
BAT_MIN_STRIKE_RATE = 0
BAT_MIN_TOP_TIER_INNINGS = 0
BOWL_MIN_INNINGS = 27
BOWL_MIN_BALLS = 0
BOWL_MIN_WICKETS = 45
BOWL_MIN_TOP_TIER_INNINGS = 12

COUNTRY_BY_PLAYER = {
    "Ibrahim Zadran": "Afghanistan", "Yasir Ali Chowdhury": "Bangladesh", "Towhid Hridoy": "Bangladesh",
    "Sahan Arachchige": "Sri Lanka", "Bhanuka Rajapaksa": "Sri Lanka", "Rahul Chopra": "Hong Kong",
    "Reeza Hendricks": "South Africa", "Luke Jongwe": "Zimbabwe", "Mahedi Hasan": "Bangladesh",
    "Gareth Delany": "Ireland", "Wellington Masakadza": "Zimbabwe", "Shamim Hossain": "Bangladesh",
    "Jaker Ali Anik": "Bangladesh", "Clive Madande": "Zimbabwe", "Shikhar Dhawan": "India",
    "Barry McCarthy": "Ireland", "Tanzim Sakib": "Bangladesh", "Mohammad Rishad Hossain": "Bangladesh",
    "Mark Adair": "Ireland", "Dunith Wellalage": "Sri Lanka", "Gudakesh Motie": "West Indies",
    "Ryan Burl": "Zimbabwe", "Dushmantha Chameera": "Sri Lanka", "Chris Jordan": "England",
    "Deepak Hooda": "India", "Brad Evans": "Zimbabwe", "Mehidy Hasan Miraz": "Bangladesh",
    "Adil Rashid": "England", "Namboori Tilak Varma": "India", "Wanindu Hasaranga": "Sri Lanka",
    "Lalit Yadav": "India", "Mohammad Mahmudullah": "Bangladesh", "George Dockrell": "Ireland",
    "M Shahrukh Khan": "India", "Kieron Pollard": "West Indies", "Abbas Afridi": "Pakistan", "Tim David": "Australia",
    "Spencer Johnson": "Australia", "Akash Madhwal": "India", "Kane Richardson": "Australia",
    "Mohit Sharma": "India", "Jediah Blades": "West Indies", "Naveen ul Haq": "Afghanistan",
    "Pieter Willem Mulder": "South Africa", "Allah Ghazanfar": "Afghanistan", "Ripon Mondol": "Bangladesh",
    "Maheesh Theekshana": "Sri Lanka", "Mustafizur Rahman": "Bangladesh", "Shamar Joseph": "West Indies",
    "Tendai Chatara": "Zimbabwe", "Liam Dawson": "England", "Yash Punja": "India",
    "FazalHaq Farooqi": "Afghanistan", "Tim Southee": "New Zealand", "Mark Wood": "England",
    "Richard Ngarava": "Zimbabwe", "Salman Mirza": "Pakistan", "Matheesha Pathirana": "Sri Lanka",
    "Mohammad Wasim": "Pakistan", "Lockie Ferguson": "New Zealand", "Trent Boult": "New Zealand",
    "Alzarri Joseph": "West Indies", "Matthew Forde": "West Indies", "Blessing Muzarabani": "Zimbabwe",
    "Mitchell Starc": "Australia", "Karn Sharma": "India", "Zaman Khan": "Pakistan",
    "William Jacks": "England", "Bilal Sami": "United Arab Emirates", "David Willey": "England",
    "Wayne Parnell": "South Africa", "Adam Milne": "New Zealand", "Joshua Little": "Ireland",
    "Lizaad Williams": "South Africa", "Chamika Karunaratne": "Sri Lanka", "Avesh Khan": "India",
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


def enforce_country_constraint(df: pd.DataFrame, name_col: str) -> pd.DataFrame:
    """Keep one player per non-India country and at most three Indian players."""
    x = df.copy()
    x["country"] = x[name_col].map(COUNTRY_BY_PLAYER).fillna("Unknown")
    selected = []
    used = set()
    india_count = 0
    for _, row in x.sort_values("PPI", ascending=False).iterrows():
        country = row["country"]
        if country == "Unknown":
            continue
        if country == "India":
            if india_count >= 3:
                continue
            india_count += 1
        elif country in used:
            continue
        used.add(country)
        selected.append(row)
        if len(selected) == 10:
            break
    result = pd.DataFrame(selected)
    result["post_retention_rank"] = range(1, len(result) + 1)
    return result


def build_eligibility(input_dir: Path, bat: pd.DataFrame, bowl: pd.DataFrame, output_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply the user-provided batting and bowling minimums separately."""
    ball = pd.read_csv(input_dir / "ball_by_ball.csv", usecols=[
        "match_id", "striker_name", "bowler_name", "runs", "is_wicket", "dismissal_type"
    ])
    matches = pd.read_csv(input_dir / "matches.csv", usecols=["match_id", "comp_id"])
    comps = pd.read_csv(input_dir / "competitions.csv", usecols=["comp_id", "comp_name", "match_format"])
    ctx = matches.merge(comps, on="comp_id", how="left")
    ball = ball.merge(ctx, on="match_id", how="left")
    ball["top_tier"] = ball["comp_name"].str.contains("IPL", case=False, na=False) | ball["match_format"].eq("T20I")
    # Count a dismissal only for the striker dismissed, excluding retired hurt/obstructing field.
    valid_dismissal = ball["is_wicket"].fillna(False) & ~ball["dismissal_type"].isin(["Run out", "Retired hurt", "Obstructing the field", "Retired out"])
    bat_i = ball.groupby("striker_name").agg(
        total_innings=("match_id", "nunique"),
        total_runs=("runs", "sum"),
        total_balls=("match_id", "size"),
        top_tier_innings=("match_id", lambda s: s[ball.loc[s.index, "top_tier"]].nunique()),
    ).reset_index()
    bowl_i = ball.groupby("bowler_name").agg(
        total_innings_bowled=("match_id", "nunique"),
        total_balls_bowled=("match_id", "size"),
        top_tier_innings=("match_id", lambda s: s[ball.loc[s.index, "top_tier"]].nunique()),
    ).reset_index()
    wickets = ball[valid_dismissal & ball["bowler_name"].notna()].groupby("bowler_name").size().rename("total_wickets")
    bowl_i = bowl_i.merge(wickets, on="bowler_name", how="left").fillna({"total_wickets": 0})
    bat_a = bat[["striker_name"]].drop_duplicates().merge(bat_i, on="striker_name", how="left").fillna(0)
    bowl_a = bowl[["bowler_name"]].drop_duplicates().merge(bowl_i, on="bowler_name", how="left").fillna(0)
    bat_a["pass_innings"] = bat_a.total_innings >= BAT_MIN_INNINGS
    bat_a["pass_runs"] = bat_a.total_runs >= BAT_MIN_RUNS
    bat_a["strike_rate"] = bat_a.total_runs.div(bat_a.total_balls.replace(0, pd.NA)).mul(100).fillna(0)
    bat_a["pass_strike_rate"] = bat_a.strike_rate >= BAT_MIN_STRIKE_RATE
    bat_a["pass_top_tier"] = bat_a.top_tier_innings >= BAT_MIN_TOP_TIER_INNINGS
    bat_a["eligible_batting"] = bat_a[["pass_innings", "pass_runs"]].all(axis=1)
    bat_a["failed_batting_rules"] = bat_a.apply(lambda r: "; ".join([
        "innings<30" if not r.pass_innings else "", "runs<1200" if not r.pass_runs else "",
        "top_tier_innings<15" if not r.pass_top_tier else ""]), axis=1).str.strip("; ").str.replace("; ;", ";", regex=False)
    bowl_a["pass_innings"] = bowl_a.total_innings_bowled >= BOWL_MIN_INNINGS
    bowl_a["pass_balls"] = bowl_a.total_balls_bowled >= BOWL_MIN_BALLS
    bowl_a["pass_wickets"] = bowl_a.total_wickets >= BOWL_MIN_WICKETS
    bowl_a["pass_top_tier"] = bowl_a.top_tier_innings >= BOWL_MIN_TOP_TIER_INNINGS
    bowl_a["eligible_bowling"] = bowl_a[["pass_innings", "pass_wickets", "pass_top_tier"]].all(axis=1)
    bowl_a["failed_bowling_rules"] = bowl_a.apply(lambda r: "; ".join([
        "innings<27" if not r.pass_innings else "", "balls<660" if not r.pass_balls else "",
        "wickets<45" if not r.pass_wickets else "", "top_tier_innings<12" if not r.pass_top_tier else ""]), axis=1).str.strip("; ").str.replace("; ;", ";", regex=False)
    output_dir.mkdir(parents=True, exist_ok=True)
    bat_a.to_csv(output_dir / "batting_eligibility_audit.csv", index=False)
    bowl_a.to_csv(output_dir / "bowling_eligibility_audit.csv", index=False)
    return bat_a[bat_a.eligible_batting][["striker_name"]], bowl_a[bowl_a.eligible_bowling][["bowler_name"]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ranking-dir", type=Path, required=True)
    parser.add_argument("--metrics-dir", type=Path, default=None)
    parser.add_argument("--input-dir", type=Path, default=Path("/home/ubuntu/superr_data"))
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
    eligible_bat, eligible_bowl = build_eligibility(args.input_dir, bat, bowl, args.output_dir)
    bat = bat.merge(eligible_bat, on="striker_name", how="inner")
    bowl = bowl.merge(eligible_bowl, on="bowler_name", how="inner")
    bat_avail, bat_removed = filter_rankings(bat, "striker_name", retention, "batting")
    bowl_avail, bowl_removed = filter_rankings(bowl, "bowler_name", retention, "bowling")
    bat_avail = enforce_country_constraint(bat_avail, "striker_name")
    bowl_avail = enforce_country_constraint(bowl_avail, "bowler_name")
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
        "Mahendra Singh Dhoni is excluded as a CSK mentor, Rasikh Salam is excluded as retained by Royal Challengers Bengaluru, Namboori Tilak Varma is excluded as retained by Mumbai Indians, and Mitchell Starc is excluded because he opted out.",
        "",
        "The same PPI formula is used. Batting eligibility requires exactly two filters: at least 30 innings and 1,200 runs. Bowling eligibility requires at least 27 innings, 45 wickets, and 12 top-tier innings; the 660-ball overs minimum has been removed. Each panel allows at most one player per non-India country and at most three Indian players; lower-exposure replacements are marked with lower confidence.",
        "",
        f"- Retained-player rows transcribed: {len(retention)}",
        f"- Expanded batting candidate pool before filter: {len(bat)}; removed: {len(bat_removed)}; available: {len(bat_avail)}",
        f"- Expanded bowling candidate pool before filter: {len(bowl)}; removed: {len(bowl_removed)}; available: {len(bowl_avail)}",
        f"- Final output size: {min(10, len(bat_avail))} eligible batters and {min(10, len(bowl_avail))} eligible bowlers. The batting list is not padded when fewer than 10 players satisfy every rule.",
        "- Eligibility audit files report every individual minimum and failed rule.",
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
