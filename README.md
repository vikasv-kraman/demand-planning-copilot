# AI Demand Planning Copilot
### KRAMAN Corp — Supply Chain AI Solutions

---

## What This Does

Upload a demand forecast (or use built-in demo data) and get instant AI-generated:

- **Exception Summary** — ranked alerts with root cause analysis
- **Executive Email Draft** — ready-to-send leadership update
- **Planner Recommendations** — week-by-week action plan
- **Risk Analysis** — supply chain risk register with mitigations

Built for: Industrial & High-Tech manufacturers (semiconductors, electronics, contract manufacturing)

---

## Quick Start (Local)

```bash
# 1. Clone or download this folder
# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py

# 4. Open browser → http://localhost:8501
```

---

## Deploy to Streamlit Cloud (Free)

1. Push this folder to a GitHub repo
2. Go to → https://share.streamlit.io
3. Connect your repo, set main file as `app.py`
4. Deploy — you get a public URL instantly

**No server needed. No cost.**

---

## API Key

You need an Anthropic API key for the AI features:
1. Go to → https://console.anthropic.com
2. Create an API key
3. Paste it in the app's Configuration section

**Estimated cost:** $5–15/month for demo use

---

## Upload Your Own Data

CSV or Excel with these columns:

| Column | Type | Example |
|--------|------|---------|
| week | date | 2024-01-07 |
| sku | text | MCU-STM32-H7 |
| description | text | STM32 Microcontroller |
| category | text | Semiconductors |
| supplier | text | STMicroelectronics |
| lead_time_weeks | number | 18 |
| safety_stock | number | 500 |
| unit_cost | number | 12.40 |
| forecast_qty | number | 850 |
| actual_qty | number | 920 (blank for future weeks) |
| on_hand_qty | number | 1200 |
| on_order_qty | number | 500 |

---

## Stack

- **UI & Hosting:** Streamlit + Streamlit Community Cloud
- **AI Engine:** Claude claude-sonnet-4-6 (Anthropic)
- **Charts:** Plotly
- **Data:** Pandas + NumPy

---

*KRAMAN Corp · AI-Powered Supply Chain Solutions*
