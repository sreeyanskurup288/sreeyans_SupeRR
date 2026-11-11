## `ball_by_ball.csv`

| Column | Type | Missing | Unique |
|---|---|---:|---:|

| `match_id` | `int64` | 0 | 867 |

| `innings` | `int64` | 0 | 4 |

| `overid` | `int64` | 0 | 20 |

| `over_ball_num` | `int64` | 0 | 13 |

| `innings_ball_num` | `int64` | 0 | 136 |

| `batting_team_id` | `int64` | 0 | 38 |

| `bowling_team_id` | `int64` | 0 | 38 |

| `striker_id` | `int64` | 0 | 888 |

| `striker_name` | `str` | 0 | 885 |

| `non_striker_id` | `int64` | 0 | 867 |

| `non_striker_name` | `str` | 0 | 864 |

| `bowler_id` | `int64` | 0 | 647 |

| `bowler_name` | `str` | 0 | 646 |

| `batting_type` | `str` | 0 | 2 |

| `bowling_type` | `str` | 0 | 12 |

| `batting_order` | `int64` | 0 | 13 |

| `runs` | `int64` | 0 | 7 |

| `is_four` | `bool` | 0 | 2 |

| `is_six` | `bool` | 0 | 2 |

| `is_wicket` | `bool` | 0 | 2 |

| `dismissal_type_id` | `float64` | 190118 | 8 |

| `dismissal_type` | `str` | 190118 | 9 |

| `dismissed_player_id` | `float64` | 190107 | 814 |

| `extras_type` | `str` | 189167 | 6 |

| `extras1_runs` | `int64` | 0 | 7 |

| `extras_2_runs` | `int64` | 0 | 3 |

| `pace_or_spin` | `str` | 0 | 2 |

| `bowl_speed` | `float64` | 0 | 1033 |

| `stroke` | `str` | 6158 | 30 |

| `delivery_style` | `str` | 391 | 34 |

| `over_or_around` | `str` | 407 | 2 |

| `on_or_off` | `str` | 0 | 2 |

| `delivery_ist_time` | `str` | 0 | 200826 |



## `competition_team_player_mapping.csv`

| Column | Type | Missing | Unique |
|---|---|---:|---:|

| `comp_id` | `int64` | 0 | 140 |

| `comp_name` | `str` | 0 | 140 |

| `team_id` | `int64` | 0 | 38 |

| `team_name` | `str` | 0 | 38 |

| `player_id` | `int64` | 0 | 1217 |

| `player_name` | `str` | 0 | 1210 |



## `competitions.csv`

| Column | Type | Missing | Unique |
|---|---|---:|---:|

| `comp_id` | `int64` | 0 | 141 |

| `comp_name` | `str` | 0 | 141 |

| `match_format` | `str` | 0 | 2 |

| `season` | `str` | 0 | 8 |



## `matches.csv`

| Column | Type | Missing | Unique |
|---|---|---:|---:|

| `match_id` | `int64` | 0 | 883 |

| `comp_id` | `int64` | 0 | 138 |

| `match_number` | `int64` | 0 | 75 |

| `match_date` | `str` | 0 | 686 |

| `stage` | `str` | 0 | 7 |

| `venue_id` | `int64` | 0 | 98 |

| `venue_country` | `str` | 0 | 17 |

| `home_team_id` | `int64` | 0 | 36 |

| `home_team` | `str` | 0 | 36 |

| `away_team_id` | `int64` | 0 | 36 |

| `away_team` | `str` | 0 | 36 |

| `home_team_captain_id` | `float64` | 44 | 89 |

| `away_team_captain_id` | `float64` | 45 | 98 |

| `toss_win_team_id` | `float64` | 15 | 37 |

| `toss_opted` | `str` | 15 | 2 |

| `man_of_the_match` | `int64` | 0 | 293 |

| `first_inn_revised_overs` | `float64` | 858 | 13 |

| `second_inn_revised_overs` | `float64` | 858 | 12 |

| `revised_target` | `float64` | 860 | 23 |

| `knock_out` | `int64` | 0 | 2 |

| `win_team_id` | `float64` | 41 | 36 |

| `result` | `str` | 0 | 670 |



## `playing_eleven.csv`

| Column | Type | Missing | Unique |
|---|---|---:|---:|

| `match_id` | `int64` | 0 | 880 |

| `team_id` | `int64` | 0 | 38 |

| `player_id` | `int64` | 0 | 1082 |

| `batting_order` | `float64` | 8678 | 13 |

| `is_played` | `bool` | 0 | 2 |

| `is_captain` | `object` | 8667 | 2 |

| `is_wk` | `object` | 8667 | 2 |

| `is_impact` | `int64` | 0 | 2 |

| `is_impact_off` | `int64` | 0 | 2 |



## `teams.csv`

| Column | Type | Missing | Unique |
|---|---|---:|---:|

| `comp_id` | `int64` | 0 | 141 |

| `team_id` | `int64` | 0 | 38 |

| `team_name` | `str` | 0 | 38 |


