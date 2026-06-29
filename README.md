# Football Value Hunter

📋 Documentação interna e índice de portfólio mantidos em repositório privado.

Bot quantitativo de value betting em futebol. Corre diariamente às 06:00 UTC, analisa odds de mercado contra probabilidades calculadas por modelo estatístico, e notifica via Telegram quando deteta uma oportunidade com vantagem real.

---

## Como funciona

### Pipeline de execução

```
Dados históricos (2 épocas)
        │
        ▼
Modelo Dixon-Coles (penaltyblog)
        │ probabilidade modelo Over 2.5
        ▼
Odds de mercado (BSD Football API)
        │ remove margem do bookmaker (Método de Shin)
        ▼
Edge = P(modelo) − P(mercado limpo)
        │
    Edge ≥ 2%?
       ├── SIM → Sinal enviado via Telegram
       └── NÃO → Rejeitado, registado no dashboard
```

### Componentes

| Módulo | Ficheiro | Função |
|---|---|---|
| Orquestrador | `main.py` | Coordena todas as etapas e exporta `docs/results.json` |
| Dados históricos | `src/data_fusion.py` | Agrega dados de Understat e football-data.co.uk |
| Motor estatístico | `src/advanced_engine.py` | Modelo Dixon-Coles + Método de Shin |
| Odds ao vivo | `src/bsd_connector.py` | Consome a BSD Football API (Over/Under 2.5 consenso) |
| Notificações | `src/notifier.py` | Envia sinal formatado para Telegram |
| Configuração | `config/settings.py` | Ligas ativas, mapeamento de equipas, limiares |

---

## Ligas monitorizadas

| Liga | Fonte histórica | BSD ID |
|---|---|---|
| Premier League (ENG) | Understat | 1 |
| La Liga (ESP) | Understat | 3 |
| Bundesliga (DEU) | Understat | 5 |
| Serie A (ITA) | Understat | 4 |
| Ligue 1 (FRA) | Understat | 6 |
| Eredivisie (NED) | football-data.co.uk | 10 |
| Liga Portugal | football-data.co.uk | 2 |
| Scottish Premiership | football-data.co.uk | 13 |
| Süper Lig (TUR) | football-data.co.uk | 11 |
| Pro League (BEL) | football-data.co.uk | 14 |

---

## Modelo estatístico

### Dixon-Coles Goal Model
Modelo probabilístico que aprende os padrões de golos marcados e sofridos de cada equipa ao longo das últimas 2 épocas. Gera uma matriz de probabilidades para todos os resultados possíveis (0-0, 0-1, 1-0, ...).

A partir dessa matriz calcula:
- **P(Over 2.5)** — probabilidade de mais de 2 golos no total
- **P(BTTS)** — probabilidade de ambas as equipas marcarem

### Método de Shin
Remove a margem do bookmaker das odds brutas de mercado para obter a probabilidade implícita real (clean probability). Mais preciso do que a simples normalização de overround.

### Cálculo do Edge
```
Edge = P_modelo(Over 2.5) − P_mercado_limpo(Over 2.5)
```
Um sinal só é gerado se `Edge ≥ 2%` e o overround de mercado for `≤ 8%`.

---

## Notificações Telegram

Quando um sinal é detetado, é enviada uma mensagem com este formato:

```
🚨 SINAL QUANTITATIVO: OVER 2.5 GOLOS 🚨

⚽ Partida: Equipa A vs Equipa B
📊 Probabilidade do Modelo: 62.4%
🎯 Odd Justa Calculada: 1.60
💰 Odd Bruta de Mercado: 1.75
📈 Margem de Vantagem (Edge): +5.20%

🤖 Projeção BTTS (Ambas Marcam):
    • Probabilidade: 54.1%
    • Odd Justa Limite: 1.85

🐳 Filtro de Preço: Método de Shin aplicado com sucesso.
```

**Só recebes notificação quando há valor real** — dias sem jogos ou sem edge suficiente passam em silêncio.

---

## Automação

O bot corre automaticamente via GitHub Actions:

- **Horário:** 06:00 UTC todos os dias
- **Manual:** disponível em Actions → "Run workflow"
- **Após cada run:** `docs/results.json` é atualizado e o dashboard republica automaticamente

### Workflow (`automation.yml`)

```
1. Checkout do código
2. Setup Python 3.11
3. Instalar dependências (penaltyblog, pandas, requests, ...)
4. Executar pipeline (main.py)
5. Commit e push do results.json atualizado
```

---

## Dashboard

Disponível em **GitHub Pages** (`/docs/index.html`). Carrega `results.json` via JavaScript e apresenta:

- Data/hora do último run
- Sinais de valor detetados (cards destacados)
- Tabela de todas as partidas analisadas com métricas Dixon-Coles

---

## Configuração (secrets necessários)

Definidos em `Settings → Secrets → Actions` do repositório:

| Secret | Descrição |
|---|---|
| `BSD_API_KEY` | Chave da BSD Football API (odds ao vivo) |
| `TELEGRAM_TOKEN` | Token do bot Telegram |
| `TELEGRAM_CHAT_ID` | ID do chat/canal para onde enviar os sinais |

---

## Parâmetros do modelo

Definidos em `config/settings.py`:

| Parâmetro | Valor | Descrição |
|---|---|---|
| `MIN_EDGE_REQUIRED` | `0.02` | Edge mínimo para gerar sinal (2%) |
| `MAX_OVERROUND_ALLOWED` | `0.08` | Overround máximo aceite (8%) |
| `seasons` | `[2024, 2025]` | Épocas usadas para treinar o modelo |

---

## Estrutura do repositório

```
football-value-hunter/
├── main.py                        # Orquestrador principal
├── config/
│   └── settings.py                # Ligas, mapeamentos, limiares
├── src/
│   ├── advanced_engine.py         # Dixon-Coles + Shin
│   ├── bsd_connector.py           # BSD Football API
│   ├── data_fusion.py             # Understat + football-data.co.uk
│   └── notifier.py                # Telegram
├── docs/
│   ├── index.html                 # Dashboard (GitHub Pages)
│   ├── results.json               # Output do pipeline (auto-gerado)
│   └── .nojekyll
└── .github/workflows/
    └── automation.yml             # Cron diário + workflow_dispatch
```
