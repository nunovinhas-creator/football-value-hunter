import os

ACTIVE_LEAGUES = {
    "EPL": {
        "understat": "ENG Premier League",
        "bsd_id": "EPL_PREMIER_LEAGUE",
        "seasons": [2024, 2025]
    }
}

TEAM_NAME_MAPPING = {
    "Man United": "Manchester United",
    "Man City": "Manchester City",
    "Tottenham Hotspur": "Tottenham",
    "Wolves": "Wolverhampton",
    "Newcastle United": "Newcastle",
    "West Ham United": "West Ham",
    "Leicester City": "Leicester",
    "Nottingham Forest": "Nottingham Forest"
}

MIN_EDGE_REQUIRED = 0.02
MAX_OVERROUND_ALLOWED = 0.08
