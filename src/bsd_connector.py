import os
import requests
from datetime import datetime
from config.settings import TEAM_NAME_MAPPING


class BSDOddsAPIConnector:
    def __init__(self):
        self.api_key = os.getenv("BSD_API_KEY")
        self.base_url = "https://api.betsapi.com/v3"

    def _get(self, endpoint: str, params: dict) -> dict:
        if not self.api_key:
            print("❌ Erro: BSD_API_KEY ausente no ambiente de execução do sistema.")
            return {}
        params["token"] = self.api_key
        try:
            r = requests.get(f"{self.base_url}{endpoint}", params=params, timeout=12)
            if r.status_code != 200:
                print(f"⚠️ BetsAPI retornou código {r.status_code}: {r.text[:200]}")
                return {}
            payload = r.json()
            if not payload.get("success"):
                print(f"⚠️ BetsAPI success=0: {payload}")
                return {}
            return payload
        except Exception as e:
            print(f"❌ Falha crítica de conexão com a API da BSD: {e}")
            return {}

    def get_live_market_fixtures(self, bsd_league_id: str) -> list:
        """
        Dois passos: lista de eventos do dia → odds Over/Under 2.5 por evento.
        """
        today = datetime.utcnow().strftime("%Y%m%d")
        events_payload = self._get("/events/upcoming", {
            "sport_id": 1,
            "league_id": bsd_league_id,
            "day": today,
        })

        processed_fixtures = []
        for event in events_payload.get("results", []):
            raw_home = event.get("home", {}).get("name", "")
            raw_away = event.get("away", {}).get("name", "")
            event_id = event.get("id")

            if not event_id or not raw_home or not raw_away:
                continue

            home = TEAM_NAME_MAPPING.get(raw_home, raw_home)
            away = TEAM_NAME_MAPPING.get(raw_away, raw_away)

            odds = self._fetch_over_under_odds(event_id)
            if odds:
                processed_fixtures.append({"home": home, "away": away, "odds": odds})

        return processed_fixtures

    def _fetch_over_under_odds(self, event_id: str) -> dict:
        """Extrai odds Over/Under 2.5 do endpoint de prematch da BetsAPI v3."""
        payload = self._get("/bet365/prematch", {"FI": event_id})
        results = payload.get("results", {})
        sp = results.get("SP", {})

        # Goal Lines market no formato Bet365 da BetsAPI
        goal_lines = sp.get("goal_lines", {})
        odds_list = goal_lines.get("odds", [])

        over_25 = None
        under_25 = None

        for odd in odds_list:
            # O handicap/name identifica a linha (ex: "2.5")
            line = str(odd.get("name", odd.get("handicap", "")))
            if line != "2.5":
                continue
            header = odd.get("header", "").lower()
            try:
                value = float(odd.get("odds", 0))
            except (ValueError, TypeError):
                continue
            if "over" in header:
                over_25 = value
            elif "under" in header:
                under_25 = value

        if over_25 and under_25:
            return {"over_25": over_25, "under_25": under_25}
        return {}
