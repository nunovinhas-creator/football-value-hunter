import io
import requests
import penaltyblog as pb
import pandas as pd


class MultiSourceDataFusion:
    def __init__(self):
        self.elo_scraper = pb.scrapers.ClubElo()

    def fetch_clean_historical_data(self, league_config: dict) -> pd.DataFrame:
        seasons = league_config["seasons"]

        if league_config.get("understat"):
            return self._fetch_understat(league_config["understat"], seasons)

        if league_config.get("footballdata"):
            return self._fetch_footballdata(league_config["footballdata"], seasons)

        return pd.DataFrame()

    def _fetch_understat(self, league_name: str, seasons: list) -> pd.DataFrame:
        all_fixtures = []
        for season in seasons:
            season_str = f"{season}-{season + 1}"
            try:
                scraper = pb.scrapers.Understat(competition=league_name, season=season_str)
                fixtures = scraper.get_fixtures()
                all_fixtures.append(fixtures)
            except Exception as e:
                print(f"⚠️ Erro ao consumir época {season_str} da liga {league_name}: {e}")

        if not all_fixtures:
            return pd.DataFrame()

        combined_df = pd.concat(all_fixtures, ignore_index=True)
        played = combined_df[pd.to_numeric(combined_df["goals_home"], errors="coerce").notna()].copy()

        return pd.DataFrame({
            "home_team": played["team_home"].values,
            "away_team": played["team_away"].values,
            "home_goals": pd.to_numeric(played["goals_home"]).astype(int).values,
            "away_goals": pd.to_numeric(played["goals_away"]).astype(int).values,
        })

    def _fetch_footballdata(self, code: str, seasons: list) -> pd.DataFrame:
        """Busca dados históricos via football-data.co.uk (CSV gratuito)."""
        all_fixtures = []
        for season in seasons:
            season_code = f"{str(season)[2:]}{str(season + 1)[2:]}"
            url = f"https://www.football-data.co.uk/mmz4281/{season_code}/{code}.csv"
            try:
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                df = pd.read_csv(io.StringIO(r.text))
                all_fixtures.append(df)
            except Exception as e:
                print(f"⚠️ Erro ao consumir football-data.co.uk {code} época {season}: {e}")

        if not all_fixtures:
            return pd.DataFrame()

        combined = pd.concat(all_fixtures, ignore_index=True)
        played = combined[pd.to_numeric(combined["FTHG"], errors="coerce").notna()].copy()

        return pd.DataFrame({
            "home_team": played["HomeTeam"].values,
            "away_team": played["AwayTeam"].values,
            "home_goals": pd.to_numeric(played["FTHG"]).astype(int).values,
            "away_goals": pd.to_numeric(played["FTAG"]).astype(int).values,
        })

    def fetch_team_elo_coefficient(self, team_name: str) -> float:
        """Retorna o rating purificado do ClubElo para modelagem secundária de força."""
        try:
            elo_df = self.elo_scraper.get_team_history(team_name)
            if not elo_df.empty:
                return float(elo_df.sort_values(by="date", ascending=False).iloc[0]["elo"])
        except Exception as e:
            print(f"⚠️ Não foi possível obter o coeficiente Elo para {team_name}: {e}")
        return 1500.0
