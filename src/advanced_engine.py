import penaltyblog as pb
import pandas as pd
from config.settings import MIN_EDGE_REQUIRED


class AdvancedMarketEngine:
    def __init__(self, historical_training_data: pd.DataFrame):
        self.model = pb.models.DixonColesGoalModel()
        self.model.fit(
            historical_training_data["home_team"],
            historical_training_data["away_team"],
            historical_training_data["home_goals"],
            historical_training_data["away_goals"]
        )

    def evaluate_true_value(self, home_team: str, away_team: str, market_odds: dict) -> dict:
        """
        Executa predições na matriz estocástica de golos, remove a margem e valida o valor (EV+).
        """
        try:
            predictions = self.model.predict(home_team, away_team)

            model_prob_over_25 = predictions.over_under(2.5)["over"]

            prob_home_0 = predictions.home_goals(0)
            prob_away_0 = predictions.away_goals(0)
            prob_0_0 = predictions.score(0, 0)
            model_prob_btts = 1 - (prob_home_0 + prob_away_0 - prob_0_0)

            odds_list = [market_odds["over_25"], market_odds["under_25"]]
            shin_decoder = pb.implied.shin(odds_list)
            clean_market_prob_over = shin_decoder["probabilities"][0]

            edge = model_prob_over_25 - clean_market_prob_over
            has_value = edge >= MIN_EDGE_REQUIRED

            return {
                "home": home_team,
                "away": away_team,
                "prob_over_25": model_prob_over_25,
                "prob_btts": model_prob_btts,
                "clean_market_prob_over": clean_market_prob_over,
                "has_value_over_25": has_value,
                "edge": edge,
                "fair_odd_over": 1 / model_prob_over_25 if model_prob_over_25 > 0 else 0,
                "fair_odd_btts": 1 / model_prob_btts if model_prob_btts > 0 else 0
            }

        except Exception as e:
            print(f"⚠️ Falha no processamento matemático de {home_team} vs {away_team}: {e}")
            return None
