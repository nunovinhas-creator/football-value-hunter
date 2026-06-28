import penaltyblog as pb
import pandas as pd
from config.settings import MIN_EDGE_REQUIRED


class AdvancedMarketEngine:
    def __init__(self, historical_training_data: pd.DataFrame):
        # penaltyblog >= 1.1.0: dados passados no construtor, sem método fit()
        self.model = pb.models.DixonColesGoalModel(
            goals_home=historical_training_data["home_goals"],
            goals_away=historical_training_data["away_goals"],
            teams_home=historical_training_data["home_team"],
            teams_away=historical_training_data["away_team"],
        )

    def evaluate_true_value(self, home_team: str, away_team: str, market_odds: dict) -> dict:
        """
        Executa predições na matriz estocástica de golos, remove a margem e valida o valor (EV+).
        """
        try:
            predictions = self.model.predict(home_team, away_team)

            # totals(line) retorna (under, push, over) — índice 2 é o Over
            model_prob_over_25 = predictions.totals(2.5)[2]

            # BTTS: P(ambas marcam) = 1 - P(home=0) - P(away=0) + P(0-0)
            prob_home_0 = predictions.home_goal_distribution()[0]
            prob_away_0 = predictions.away_goal_distribution()[0]
            prob_0_0 = predictions.exact_score(0, 0)
            model_prob_btts = 1 - (prob_home_0 + prob_away_0 - prob_0_0)

            # Método de Shin via calculate_implied
            shin_result = pb.implied.calculate_implied(
                [market_odds["over_25"], market_odds["under_25"]],
                method="SHIN"
            )
            clean_market_prob_over = shin_result.probabilities[0]

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
