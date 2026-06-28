import sys
import json
import os
from datetime import datetime, timezone
from config.settings import ACTIVE_LEAGUES
from src.data_fusion import MultiSourceDataFusion
from src.bsd_connector import BSDOddsAPIConnector
from src.advanced_engine import AdvancedMarketEngine
from src.notifier import TelegramSignalNotifier


def run_quantitative_pipeline():
    print("🤖 Inicializando Bot Quantitativo de Value Hunting [Penaltyblog Core]...")

    data_fusion = MultiSourceDataFusion()
    bsd_feed = BSDOddsAPIConnector()
    notifier = TelegramSignalNotifier()

    dashboard = {
        "last_run": datetime.now(timezone.utc).isoformat(),
        "leagues_processed": [],
        "signals": [],
        "analyzed": [],
        "total_matches_analyzed": 0,
        "total_signals": 0,
    }

    for league_key, config in ACTIVE_LEAGUES.items():
        print(f"\n🔄 Processando liga parametrizada: {league_key}")

        historical_df = data_fusion.fetch_clean_historical_data(config)
        if historical_df.empty:
            print(f"❌ Erro Crítico: Base histórica vazia para a liga {league_key}. Ignorando.")
            continue

        print(f"📊 Ajustando coeficientes estatísticos Dixon-Coles...")
        engine_math = AdvancedMarketEngine(historical_df)

        print(f"🔌 Puxando fixtures do dia corrente na API da BSD...")
        todays_fixtures = bsd_feed.get_live_market_fixtures(config["bsd_id"])

        if not todays_fixtures:
            print(f"📭 Nenhum mercado válido ou jogo ativo para hoje na liga {league_key}.")
            continue

        dashboard["leagues_processed"].append(league_key)
        print(f"🔍 Analisando {len(todays_fixtures)} partidas com aplicação do algoritmo de Shin...")
        for match in todays_fixtures:
            analysis_results = engine_math.evaluate_true_value(match["home"], match["away"], match["odds"])

            if not analysis_results:
                continue

            dashboard["total_matches_analyzed"] += 1
            record = {
                **analysis_results,
                "league": league_key,
                "market_odd_over": match["odds"]["over_25"],
                "market_odd_under": match["odds"]["under_25"],
            }

            print(f"-> {analysis_results['home']} vs {analysis_results['away']} | Edge Analisado: {analysis_results['edge']*100:.2f}%")

            if analysis_results["has_value_over_25"]:
                print("   🚨 [VALOR DETETADO] Encaminhando sinal para o Telegram Notifier...")
                notifier.dispatch_value_signal(analysis_results, match["odds"])
                dashboard["signals"].append(record)
                dashboard["total_signals"] += 1
            else:
                print("   ❌ Rejeitado: O preço de mercado não oferece margem estatística.")
                dashboard["analyzed"].append(record)

    os.makedirs("docs", exist_ok=True)
    with open("docs/results.json", "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)
    print("\n📊 Resultados exportados para docs/results.json")

    print("\n✅ Pipeline diária executada com sucesso.")


if __name__ == "__main__":
    try:
        run_quantitative_pipeline()
    except KeyboardInterrupt:
        print("\n❌ Operação abortada manualmente pelo utilizador.")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Falha crítica não tratada no orquestrador principal: {e}")
        sys.exit(1)
