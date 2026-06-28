import os
import requests
from config.settings import TEAM_NAME_MAPPING


class BSDOddsAPIConnector:
    def __init__(self):
        self.api_key = os.getenv("BSD_API_KEY")
        self.base_url = "https://api.bsd.com/v1"

    def get_live_market_fixtures(self, bsd_league_id: str) -> list:
        """
        Extrai os jogos agendados para o dia e as respetivas odds abertas para Over/Under 2.5.
        """
        if not self.api_key:
            print("❌ Erro: BSD_API_KEY ausente no ambiente de execução do sistema.")
            return []

        url = f"{self.base_url}/fixtures"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {
            "league": bsd_league_id,
            "date": "today",
            "markets": "over_under_2.5"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=12)
            if response.status_code != 200:
                print(f"⚠️ BSD API retornou código de estado inválido: {response.status_code}")
                return []

            payload = response.json()
            processed_fixtures = []

            for item in payload.get("results", []):
                raw_home = item.get("home_team")
                raw_away = item.get("away_team")

                home_normalized = TEAM_NAME_MAPPING.get(raw_home, raw_home)
                away_normalized = TEAM_NAME_MAPPING.get(raw_away, raw_away)

                odds_packet = item.get("odds", {})
                over_25 = float(odds_packet.get("over_2.5", 0))
                under_25 = float(odds_packet.get("under_2.5", 0))

                if over_25 > 0 and under_25 > 0:
                    processed_fixtures.append({
                        "home": home_normalized,
                        "away": away_normalized,
                        "odds": {
                            "over_25": over_25,
                            "under_25": under_25
                        }
                    })
            return processed_fixtures

        except Exception as e:
            print(f"❌ Falha crítica de conexão com a API da BSD: {e}")
            return []
