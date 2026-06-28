import penaltyblog as pb
import pandas as pd


class MultiSourceDataFusion:
    def __init__(self):
        self.elo_scraper = pb.scrapers.ClubElo()

    def fetch_clean_historical_data(self, league_name: str, seasons: list) -> pd.DataFrame:
        """
        Consome, limpa e padroniza dados históricos de golos com base no Understat.
        """
        all_fixtures = []
        for season in seasons:
            # penaltyblog >= 1.1.0: Understat requer competition e season no construtor
            # Formato da época: "2024-2025" (ano de início + ano seguinte)
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

        # Filtrar apenas jogos concluídos (goals_home não nulo)
        played = combined_df[pd.to_numeric(combined_df["goals_home"], errors="coerce").notna()].copy()

        # Colunas do penaltyblog >= 1.1.0: team_home/team_away/goals_home/goals_away
        return pd.DataFrame({
            "home_team": played["team_home"].values,
            "away_team": played["team_away"].values,
            "home_goals": pd.to_numeric(played["goals_home"]).astype(int).values,
            "away_goals": pd.to_numeric(played["goals_away"]).astype(int).values,
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
