import os
import requests
from datetime import datetime, timezone
from config.settings import TEAM_NAME_MAPPING


class BSDOddsAPIConnector:
    def __init__(self):
        self.api_key = os.getenv("BSD_API_KEY")
        self.base_url = "https://sports.bzzoiro.com"
        self.session = requests.Session()
        if self.api_key:
            self.session.headers["Authorization"] = f"Token {self.api_key}"

    def _get(self, endpoint: str, params: dict = None):
        if not self.api_key:
            print("❌ Erro: BSD_API_KEY ausente no ambiente de execução do sistema.")
            return None
        try:
            r = self.session.get(f"{self.base_url}{endpoint}", params=params, timeout=12)
            if r.status_code != 200:
                print(f"⚠️ BSD API retornou código {r.status_code}: {r.text[:300]}")
                return None
            return r.json()
        except Exception as e:
            print(f"❌ Falha crítica de conexão com a BSD API: {e}")
            return None

    def _unwrap(self, data) -> list:
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("results", [])
        return []

    def get_live_market_fixtures(self, league_id: str) -> list:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        data = self._get("/api/v2/events/", {
            "league_id": league_id,
            "date_from": today,
            "date_to": today,
            "status": "notstarted",
            "limit": 200,
        })

        processed_fixtures = []
        for event in self._unwrap(data):
            event_id = event.get("id")
            raw_home = event.get("home_team", "")
            raw_away = event.get("away_team", "")

            if not event_id or not raw_home or not raw_away:
                continue

            home = TEAM_NAME_MAPPING.get(raw_home, raw_home)
            away = TEAM_NAME_MAPPING.get(raw_away, raw_away)

            odds = self._fetch_over_under_odds(event_id)
            if odds:
                processed_fixtures.append({"home": home, "away": away, "odds": odds})

        return processed_fixtures

    def _fetch_over_under_odds(self, event_id: int) -> dict:
        """Extrai odds Over/Under 2.5 consenso via BSD Football API v2."""
        data = self._get("/api/v2/odds/", {
            "event_id": event_id,
            "market": "over_under_25",
            "bookmaker_slug": "consensus",
        })

        over_25 = None
        under_25 = None

        for item in self._unwrap(data):
            outcome = item.get("outcome", "")
            try:
                value = float(item.get("decimal_odds", 0))
            except (ValueError, TypeError):
                continue
            if outcome == "over":
                over_25 = value
            elif outcome == "under":
                under_25 = value

        if over_25 and under_25:
            return {"over_25": over_25, "under_25": under_25}
        return {}
