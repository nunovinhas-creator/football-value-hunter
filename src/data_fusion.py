import penaltyblog as pb
import pandas as pd


class MultiSourceDataFusion:
    def __init__(self):
        self.understat_scraper = pb.scrapers.Understat()
        self.elo_scraper = pb.scrapers.ClubElo()

    def fetch_clean_historical_data(self, league_name: str, seasons: list) -> pd.DataFrame:
        """
        Consome, limpa e padroniza dados históricos de golos com base no Understat.
        """
        all_fixtures = []
        for season in seasons:
            try:
                fixtures = self.understat_scraper.get_league_fixtures(league_name, season=str(season))
                all_fixtures.append(fixtures)
            except Exception as e:
                print(f"⚠️ Erro ao consumir época {season} da liga {league_name}: {e}")

        if not all_fixtures:
            return pd.DataFrame()

        combined_df = pd.concat(all_fixtures, ignore_index=True)

        return pd.DataFrame({
            "home_team": combined_df["home_team"],
            "away_team": combined_df["away_team"],
            "home_goals": combined_df["home_goals"].astype(int),
            "away_goals": combined_df["away_goals"].astype(int)
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
