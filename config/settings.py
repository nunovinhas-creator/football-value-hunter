import os

# Understat cobre: EPL, La Liga, Bundesliga, Serie A, Ligue 1
# Restantes ligas usam football-data.co.uk como fonte histórica
ACTIVE_LEAGUES = {
    "EPL":        {"understat": "ENG Premier League",  "bsd_id": "1",  "seasons": [2024, 2025]},
    "LA_LIGA":    {"understat": "ESP La Liga",         "bsd_id": "3",  "seasons": [2024, 2025]},
    "BUNDESLIGA": {"understat": "DEU Bundesliga 1",      "bsd_id": "5",  "seasons": [2024, 2025]},
    "SERIE_A":    {"understat": "ITA Serie A",         "bsd_id": "4",  "seasons": [2024, 2025]},
    "LIGUE_1":    {"understat": "FRA Ligue 1",         "bsd_id": "6",  "seasons": [2024, 2025]},
    "EREDIVISIE": {"footballdata": "N1",               "bsd_id": "10", "seasons": [2024, 2025]},
    "LIGA_PT":    {"footballdata": "P1",               "bsd_id": "2",  "seasons": [2024, 2025]},
    "SCOTLAND":   {"footballdata": "SC0",              "bsd_id": "13", "seasons": [2024, 2025]},
    "SUPER_LIG":  {"footballdata": "T1",               "bsd_id": "11", "seasons": [2024, 2025]},
    "PRO_LEAGUE": {"footballdata": "B1",               "bsd_id": "14", "seasons": [2024, 2025]},
}

TEAM_NAME_MAPPING = {
    # Understat → BSD API
    "Man United": "Manchester United",
    "Man City": "Manchester City",
    "Tottenham Hotspur": "Tottenham",
    "Wolves": "Wolverhampton",
    "Newcastle United": "Newcastle",
    "West Ham United": "West Ham",
    "Leicester City": "Leicester",
    # football-data.co.uk → BSD API (Netherlands)
    "Sp. Rotterdam": "Sparta Rotterdam",
    "NEC Nijmegen": "NEC",
    # football-data.co.uk → BSD API (Portugal)
    "Famalicao": "Famalicão",
    "Maritimo": "Marítimo",
    "Portimonense": "Portimonense SC",
    # football-data.co.uk → BSD API (Turkey)
    "Alanyaspor": "Alanya",
    "Ankaragucu": "Ankaraspor",
}

MIN_EDGE_REQUIRED = 0.02
MAX_OVERROUND_ALLOWED = 0.08
