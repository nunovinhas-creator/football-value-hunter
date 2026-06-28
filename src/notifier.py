import os
import requests


class TelegramSignalNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def dispatch_value_signal(self, metrics: dict, market_odds: dict):
        """
        Formata os dados do modelo e envia o sinal se as credenciais existirem.
        """
        if not self.token or not self.chat_id:
            print("⚠️ Notificação omitida: Variáveis de ambiente do Telegram ausentes.")
            return

        msg = (
            f"🚨 *SINAL QUANTITATIVO: OVER 2.5 GOLOS* 🚨\n\n"
            f"⚽ *Partida:* {metrics['home']} vs {metrics['away']}\n"
            f"📊 *Probabilidade do Modelo:* {metrics['prob_over_25']*100:.1f}%\n"
            f"🎯 *Odd Justa Calculada:* {metrics['fair_odd_over']:.2f}\n"
            f"💰 *Odd Bruta de Mercado (BSD):* {market_odds['over_25']:.2f}\n"
            f"📈 *Margem de Vantagem (Edge):* +{metrics['edge']*100:.2f}%\n\n"
            f"🤖 *Projeção BTTS (Ambas Marcam):*\n"
            f"    • Probabilidade: {metrics['prob_btts']*100:.1f}%\n"
            f"    • Odd Justa Limite: {metrics['fair_odd_btts']:.2f}\n\n"
            f"🐳 _Filtro de Preço: Método de Shin aplicado com sucesso._"
        )

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": msg, "parse_mode": "Markdown"}

        try:
            res = requests.post(url, json=payload, timeout=8)
            if res.status_code != 200:
                print(f"⚠️ Resposta inválida do Telegram API: {res.text}")
        except Exception as e:
            print(f"⚠️ Falha de rede ao publicar sinal no canal: {e}")
