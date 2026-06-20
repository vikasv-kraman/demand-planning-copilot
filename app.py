import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import anthropic
import json
import io


# ── KRAMAN Logo (base64 embedded) ────────────────────────────────────────────
KRAMAN_LOGO_B64 = "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"

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Demand Planning Copilot",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS — KRAMAN Dark Theme ───────────────────────────────────────────
st.markdown("""
<style>
    /* ── KRAMAN DARK PALETTE ──
       bg-deep:    #0a1628   (page background)
       bg-card:    #0d1f3c   (card surface)
       bg-raised:  #112244   (elevated elements)
       accent:     #1a6fd4   (primary blue — CTA button)
       accent-lt:  #2d9cdb   (lighter blue — logo, highlights)
       text-pri:   #ffffff
       text-sec:   #8ab4d4   (muted blue-white)
       text-dim:   #4a7fa5   (very muted)
       border:     #1e3a5f
       border-lt:  #1a3050
    */

    /* ── Global page background ── */
    .stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: #0a1628 !important;
    }
    [data-testid="stHeader"] { background-color: #0a1628 !important; }
    [data-testid="stSidebar"] { background-color: #0d1f3c !important; }
    .main .block-container { 
        padding: 2rem 2.5rem 3rem; max-width: 1400px;
        background-color: #0a1628 !important;
    }

    /* ── Global text ── */
    body, p, span, div, label { color: #ffffff; }
    h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }

    /* ── Header ── */
    .app-header {
        display: flex; align-items: center; gap: 16px;
        border-bottom: 1px solid #1e3a5f; padding-bottom: 1.25rem; margin-bottom: 2rem;
    }
    .app-logo {
        width: 42px; height: 42px; border-radius: 10px;
        background: #1a6fd4; display: flex; align-items: center;
        justify-content: center; font-size: 20px;
    }
    .app-title { font-size: 1.3rem; font-weight: 700; color: #ffffff !important; margin: 0; letter-spacing: 0.01em; }
    .app-subtitle { font-size: 0.8rem; color: #8ab4d4; margin: 0; }
    .powered-badge {
        margin-left: auto; background: #0d1f3c; border: 1px solid #1e3a5f;
        border-radius: 20px; padding: 4px 14px;
        font-size: 0.7rem; color: #8ab4d4; font-weight: 500;
    }

    /* ── Metric cards ── */
    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 2rem; }
    .metric-card {
        background: #0d1f3c; border: 1px solid #1e3a5f; border-radius: 12px;
        padding: 1.1rem 1.25rem;
    }
    .metric-label { 
        font-size: 0.72rem; color: #8ab4d4; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; 
    }
    .metric-value { font-size: 1.7rem; font-weight: 700; color: #ffffff; line-height: 1; }
    .metric-delta { font-size: 0.75rem; margin-top: 4px; }
    .delta-neg { color: #f87171; }
    .delta-pos { color: #4ade80; }
    .delta-warn { color: #fbbf24; }

    /* ── Status badges ── */
    .badge {
        display: inline-block; padding: 2px 10px; border-radius: 20px;
        font-size: 0.7rem; font-weight: 600;
    }
    .badge-red  { background: rgba(220,38,38,0.2);  color: #fca5a5; border: 1px solid rgba(220,38,38,0.4); }
    .badge-amber{ background: rgba(217,119,6,0.2);  color: #fcd34d; border: 1px solid rgba(217,119,6,0.4); }
    .badge-green{ background: rgba(22,163,74,0.2);  color: #86efac; border: 1px solid rgba(22,163,74,0.4); }
    .badge-blue { background: rgba(26,111,212,0.2); color: #93c5fd; border: 1px solid rgba(26,111,212,0.4); }

    /* ── Section headers ── */
    .section-header {
        font-size: 0.75rem; font-weight: 600; color: #4a7fa5;
        text-transform: uppercase; letter-spacing: 0.1em;
        margin: 2rem 0 1rem; border-bottom: 1px solid #1e3a5f; padding-bottom: 6px;
    }

    /* ── AI output blocks ── */
    .ai-block {
        background: #0d1f3c; border: 1px solid #1e3a5f; border-radius: 12px;
        padding: 1.5rem; margin-bottom: 1rem;
    }
    .ai-block-title {
        font-size: 0.75rem; font-weight: 600; color: #4a7fa5;
        text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 12px;
    }

    /* ── Exception table ── */
    .exc-row {
        display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
        gap: 12px; padding: 10px 0; border-bottom: 1px solid #1a3050;
        align-items: center; font-size: 0.85rem;
    }
    .exc-header {
        font-size: 0.7rem; font-weight: 600; color: #4a7fa5;
        text-transform: uppercase; letter-spacing: 0.05em;
    }

    /* ── Streamlit native component overrides ── */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 4px; background: #0d1f3c !important; border-radius: 10px; padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px; padding: 6px 16px;
        font-size: 0.82rem; font-weight: 500;
        color: #8ab4d4 !important; background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: #1a6fd4 !important; color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab-border"] { display: none !important; }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }

    /* Buttons */
    .stButton > button {
        border-radius: 8px; font-weight: 600; font-size: 0.85rem;
        border: 1px solid #1e3a5f; color: #8ab4d4;
        background: #0d1f3c;
    }
    .stButton > button:hover { border-color: #1a6fd4; color: #ffffff; background: #112244; }
    .stButton > button[kind="primary"] {
        background: #1a6fd4 !important; border-color: #1a6fd4 !important; color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover { background: #1560bc !important; }

    /* Download button */
    .stDownloadButton > button {
        border-radius: 8px; font-weight: 500; font-size: 0.85rem;
        background: #0d1f3c; border: 1px solid #1e3a5f; color: #8ab4d4;
    }
    .stDownloadButton > button:hover { border-color: #1a6fd4; color: #ffffff; }

    /* Text input */
    .stTextInput > div > div > input {
        background: #0d1f3c !important; border: 1px solid #1e3a5f !important;
        color: #ffffff !important; border-radius: 8px !important;
    }
    .stTextInput > div > div > input:focus { border-color: #1a6fd4 !important; }
    .stTextInput label { color: #8ab4d4 !important; }

    /* Selectbox */
    .stSelectbox > div > div {
        background: #0d1f3c !important; border: 1px solid #1e3a5f !important;
        border-radius: 8px !important; color: #ffffff !important;
    }
    .stSelectbox label { color: #8ab4d4 !important; }

    /* Expander */
    .streamlit-expanderHeader {
        background: #0d1f3c !important; border: 1px solid #1e3a5f !important;
        border-radius: 8px !important; color: #8ab4d4 !important;
    }
    .streamlit-expanderContent {
        background: #0d1f3c !important; border: 1px solid #1e3a5f !important;
        border-top: none !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #0d1f3c; border: 2px dashed #1e3a5f; border-radius: 12px; padding: 0.5rem;
    }
    [data-testid="stFileUploader"] label { color: #8ab4d4 !important; }

    /* Spinner */
    .stSpinner > div { border-top-color: #1a6fd4 !important; }

    /* Success / warning / error messages */
    .stSuccess { background: rgba(22,163,74,0.15) !important; border: 1px solid rgba(22,163,74,0.3) !important; color: #86efac !important; border-radius: 8px !important; }
    .stWarning { background: rgba(217,119,6,0.15) !important; border: 1px solid rgba(217,119,6,0.3) !important; color: #fcd34d !important; border-radius: 8px !important; }
    .stError   { background: rgba(220,38,38,0.15) !important; border: 1px solid rgba(220,38,38,0.3) !important; color: #fca5a5 !important; border-radius: 8px !important; }

    /* Divider */
    hr { border-color: #1e3a5f; margin: 1.5rem 0; }

    /* Email output */
    .email-output {
        font-family: Georgia, serif; font-size: 0.9rem; line-height: 1.7;
        color: #cce0f5; white-space: pre-wrap;
    }

    /* Risk items */
    .risk-item {
        display: flex; gap: 12px; padding: 12px 0;
        border-bottom: 1px solid #1a3050; align-items: flex-start;
    }
    .risk-title { font-size: 0.87rem; font-weight: 600; color: #ffffff; }
    .risk-desc  { font-size: 0.82rem; color: #8ab4d4; margin-top: 2px; }

    /* KRAMAN footer */
    .kraman-footer {
        text-align: center; padding: 2rem 0 0;
        font-size: 0.72rem; color: #1e3a5f; letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0a1628; }
    ::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #1a6fd4; }
</style>
""", unsafe_allow_html=True)


# ── Sample data generator ─────────────────────────────────────────────────────
@st.cache_data
def generate_forecast_data(seed=42):
    np.random.seed(seed)
    weeks = pd.date_range(start=datetime.now() - timedelta(weeks=12), periods=16, freq='W')
    
    skus = [
        {"sku": "MCU-STM32-H7", "desc": "STM32 H7 Microcontroller", "category": "Semiconductors", "supplier": "STMicroelectronics", "lead_time": 18, "safety_stock": 500, "unit_cost": 12.40},
        {"sku": "CAP-MLCC-0402", "desc": "MLCC Capacitor 0402 100nF", "category": "Passives", "supplier": "Murata (Japan)", "lead_time": 26, "safety_stock": 10000, "unit_cost": 0.012},
        {"sku": "PCB-MAIN-REV4", "desc": "Main PCB Rev4 Assembly", "category": "PCB Assembly", "supplier": "TTM Technologies", "lead_time": 10, "safety_stock": 200, "unit_cost": 48.90},
        {"sku": "CONN-USB-C-SMT", "desc": "USB-C SMT Connector", "category": "Connectors", "supplier": "Amphenol", "lead_time": 12, "safety_stock": 2000, "unit_cost": 0.85},
        {"sku": "FPGA-XC7A-35T", "desc": "Xilinx Artix-7 35T FPGA", "category": "Semiconductors", "supplier": "AMD/Xilinx", "lead_time": 52, "safety_stock": 150, "unit_cost": 89.00},
        {"sku": "SENS-IMU-6DOF", "desc": "6-DOF IMU Sensor Module", "category": "Sensors", "supplier": "TDK InvenSense", "lead_time": 16, "safety_stock": 300, "unit_cost": 6.20},
        {"sku": "POW-DCDC-48V", "desc": "48V DC-DC Converter Module", "category": "Power", "supplier": "Vicor Corp", "lead_time": 20, "safety_stock": 100, "unit_cost": 34.50},
        {"sku": "MEM-DDR4-8GB", "desc": "DDR4 8GB DRAM Module", "category": "Memory", "supplier": "Samsung Semi", "lead_time": 14, "safety_stock": 400, "unit_cost": 22.10},
    ]
    
    records = []
    for sku_info in skus:
        base_demand = np.random.randint(300, 2000)
        trend = np.random.uniform(-0.02, 0.05)
        
        for i, week in enumerate(weeks):
            seasonality = 1 + 0.15 * np.sin(2 * np.pi * i / 12)
            noise = np.random.normal(1, 0.12)
            spike = 1.6 if i == 9 and sku_info["sku"] == "MCU-STM32-H7" else 1.0
            
            forecast = max(0, int(base_demand * seasonality * (1 + trend * i) * spike))
            actual = max(0, int(forecast * noise)) if i < 12 else None
            
            on_hand = max(0, int(sku_info["safety_stock"] * np.random.uniform(0.3, 1.8)))
            on_order = int(forecast * np.random.uniform(0.5, 1.5)) if i >= 10 else 0
            
            records.append({
                "week": week,
                "sku": sku_info["sku"],
                "description": sku_info["desc"],
                "category": sku_info["category"],
                "supplier": sku_info["supplier"],
                "lead_time_weeks": sku_info["lead_time"],
                "safety_stock": sku_info["safety_stock"],
                "unit_cost": sku_info["unit_cost"],
                "forecast_qty": forecast,
                "actual_qty": actual,
                "on_hand_qty": on_hand,
                "on_order_qty": on_order,
                "projected_woc": round(on_hand / max(forecast / 4, 1), 1),
            })
    
    df = pd.DataFrame(records)
    df["variance_pct"] = df.apply(
        lambda r: round(((r["actual_qty"] - r["forecast_qty"]) / max(r["forecast_qty"], 1)) * 100, 1)
        if r["actual_qty"] is not None else None, axis=1
    )
    df["at_risk_value"] = df.apply(
        lambda r: round(max(0, r["safety_stock"] - r["on_hand_qty"]) * r["unit_cost"], 2), axis=1
    )
    return df


def compute_exceptions(df):
    latest_week = df[df["actual_qty"].isna()].groupby("sku").first().reset_index()
    exceptions = []
    
    for _, row in latest_week.iterrows():
        issues = []
        severity = "Low"
        
        woc = row["projected_woc"]
        if woc < 2:
            issues.append(f"Critical stock — {woc:.1f} weeks of cover")
            severity = "Critical"
        elif woc < 4:
            issues.append(f"Low stock — {woc:.1f} weeks of cover")
            severity = "High" if severity != "Critical" else severity

        if row["lead_time_weeks"] > 20:
            issues.append(f"Long lead time: {row['lead_time_weeks']}w")
            severity = "High" if severity == "Low" else severity

        hist = df[(df["sku"] == row["sku"]) & (df["actual_qty"].notna())]
        if len(hist) > 3:
            avg_var = hist["variance_pct"].abs().mean()
            if avg_var > 20:
                issues.append(f"High forecast error: {avg_var:.0f}% avg variance")
                severity = "High" if severity == "Low" else severity
        
        if row["at_risk_value"] > 5000:
            issues.append(f"${row['at_risk_value']:,.0f} inventory at risk")
            severity = "Critical" if row["at_risk_value"] > 15000 else ("High" if severity == "Low" else severity)
        
        if issues:
            exceptions.append({
                "sku": row["sku"],
                "description": row["description"],
                "category": row["category"],
                "supplier": row["supplier"],
                "severity": severity,
                "issues": issues,
                "woc": woc,
                "lead_time": row["lead_time_weeks"],
                "at_risk_value": row["at_risk_value"],
                "on_hand": row["on_hand_qty"],
                "safety_stock": row["safety_stock"],
                "forecast": row["forecast_qty"],
            })
    
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    return sorted(exceptions, key=lambda x: severity_order.get(x["severity"], 4))


# ── AI caller ─────────────────────────────────────────────────────────────────
def call_claude(prompt: str, system: str = "") -> str:
    try:
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=system or "You are a senior supply chain analyst specializing in high-tech and industrial electronics manufacturing.",
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


def generate_all_outputs(df, exceptions):
    exc_summary_text = json.dumps([{
        "sku": e["sku"], "desc": e["description"], "severity": e["severity"],
        "issues": e["issues"], "woc": e["woc"], "lead_time": e["lead_time"],
        "supplier": e["supplier"], "at_risk_value": e["at_risk_value"]
    } for e in exceptions], indent=2)
    
    skus_summary = df.groupby("sku").agg({
        "description": "first", "category": "first", "forecast_qty": "mean",
        "variance_pct": "mean", "projected_woc": "mean"
    }).round(1).to_string()

    outputs = {}

    with st.spinner("Analyzing exceptions..."):
        outputs["exception"] = call_claude(
            f"""Analyze these supply chain exceptions for an industrial high-tech manufacturer:

{exc_summary_text}

Write a crisp exception summary (3-4 sentences per critical/high item) covering:
- What's the core risk
- Root cause hypothesis
- Immediate recommended action
- Financial exposure if unaddressed

Use plain business language. No bullet points. Be direct.""",
            "You are a senior supply chain analyst. Be direct, specific, and action-oriented."
        )

    with st.spinner("Drafting executive email..."):
        outputs["email"] = call_claude(
            f"""Draft a concise executive email based on this supply chain exception data:

{exc_summary_text}

Format:
Subject: [write a sharp subject line]

[Email body - 3 short paragraphs max]
- Para 1: Situation summary (what's happening)  
- Para 2: Top 2-3 risks with dollar impact
- Para 3: Decisions needed from leadership

Sign off as: Supply Chain Operations Team
Keep it under 200 words. Executive language. No jargon."""
        )

    with st.spinner("Building planner recommendations..."):
        outputs["recommendations"] = call_claude(
            f"""Based on this demand data and exceptions, give a weekly action plan for the demand planner:

Exceptions:
{exc_summary_text}

SKU Performance:
{skus_summary}

Format as:
THIS WEEK (immediate actions - be specific with SKU names and quantities)
NEXT 2 WEEKS (medium term adjustments)
THIS MONTH (strategic actions)

Be specific. Name the SKUs. Give concrete actions like "Issue PO for X units of MCU-STM32-H7". No fluff."""
        )

    with st.spinner("Running risk analysis..."):
        outputs["risk"] = call_claude(
            f"""Perform a supply chain risk analysis for this high-tech manufacturer:

Exception data:
{exc_summary_text}

Identify and rank the top 5 risks. For each risk use EXACTLY this plain text format with no markdown, no asterisks, no bold, no hyphens as bullets:

RISK 1 - [Risk Name]
SKU: [SKU code] | Supplier: [Supplier] | Severity: [Critical/High/Medium]
Probability: [HIGH/MEDIUM/LOW] | Impact: [HIGH/MEDIUM/LOW]
Analysis: [2-3 sentence analysis of the risk and financial exposure]
Mitigation: [Specific concrete action with timeline]

RISK 2 - [Risk Name]
[same format]

Continue to RISK 5. Be specific. Reference actual SKU codes and supplier names. No markdown formatting whatsoever."""
        )

    return outputs


# ── Charts ────────────────────────────────────────────────────────────────────
def chart_forecast_vs_actual(df, sku):
    sku_df = df[df["sku"] == sku].sort_values("week")
    hist = sku_df[sku_df["actual_qty"].notna()]
    fcast = sku_df[sku_df["actual_qty"].isna()]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist["week"], y=hist["actual_qty"],
        name="Actual", line=dict(color="#0f4c81", width=2.5), mode="lines+markers",
        marker=dict(size=6)))
    fig.add_trace(go.Scatter(x=sku_df["week"], y=sku_df["forecast_qty"],
        name="Forecast", line=dict(color="#94a3b8", width=2, dash="dash"), mode="lines"))
    if not fcast.empty:
        fig.add_trace(go.Scatter(x=fcast["week"], y=fcast["forecast_qty"],
            name="Future Forecast", line=dict(color="#f59e0b", width=2.5), mode="lines+markers",
            marker=dict(size=6, symbol="diamond")))
    
    fig.update_layout(
        height=260, margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.25, font=dict(size=11)),
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#f1f5f9", tickfont=dict(size=11)),
        font=dict(family="Inter, sans-serif")
    )
    return fig


def chart_exception_heatmap(exceptions):
    if not exceptions:
        return None
    skus = [e["sku"] for e in exceptions]
    risk_scores = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    colors = {"Critical": "#dc2626", "High": "#f59e0b", "Medium": "#3b82f6", "Low": "#22c55e"}
    
    fig = go.Figure(go.Bar(
        x=[risk_scores[e["severity"]] for e in exceptions],
        y=skus, orientation="h",
        marker_color=[colors[e["severity"]] for e in exceptions],
        text=[e["severity"] for e in exceptions],
        textposition="inside", textfont=dict(size=11, color="white")
    ))
    fig.update_layout(
        height=220, margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(tickfont=dict(size=11)),
        font=dict(family="Inter, sans-serif")
    )
    return fig


# ── Main app ──────────────────────────────────────────────────────────────────
def main():
    # Header
    st.markdown(f"""
    <div class="app-header">
        <div style="display:flex;align-items:center;gap:16px">
            <img src="data:image/png;base64,{KRAMAN_LOGO_B64}" 
                 style="height:38px;width:auto;object-fit:contain;" 
                 alt="KRAMAN Corp">
            <div style="width:1px;height:36px;background:#1e3a5f;margin:0 4px;"></div>
            <div>
                <p class="app-title">AI Demand Planning Copilot</p>
                <p class="app-subtitle">Industrial & High-Tech Supply Chain Intelligence</p>
            </div>
        </div>
        <div class="powered-badge">Powered by Claude AI &nbsp;·&nbsp; KRAMAN Corp</div>
    </div>
    """, unsafe_allow_html=True)

    # API Key input
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    
    with st.expander("⚙️ Configuration", expanded=not st.session_state.api_key):
        api_input = st.text_input(
            "Anthropic API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="sk-ant-...",
            help="Get your key at console.anthropic.com"
        )
        if api_input:
            st.session_state.api_key = api_input

    # Data source
    st.markdown('<p class="section-header">Data Source</p>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload forecast file (CSV or Excel)",
            type=["csv", "xlsx", "xls"],
            help="Columns needed: SKU, forecast_qty, actual_qty, week, supplier, lead_time_weeks, on_hand_qty"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        use_demo = st.button("🎯 Generate Demo Data", type="primary", use_container_width=True)

    # Load data
    if "df" not in st.session_state:
        st.session_state.df = None
        st.session_state.exceptions = []
        st.session_state.ai_outputs = {}
        st.session_state.demo_seed = 42

    if use_demo:
        seed = st.session_state.get("demo_seed", 42)
        st.session_state.demo_seed = seed + np.random.randint(1, 5)
        st.session_state.df = generate_forecast_data(seed)
        st.session_state.exceptions = compute_exceptions(st.session_state.df)
        st.session_state.ai_outputs = {}
        st.success("✅ Demo data generated — 8 SKUs across 16 weeks, Industrial High-Tech vertical")

    elif uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                st.session_state.df = pd.read_csv(uploaded_file, parse_dates=["week"])
            else:
                st.session_state.df = pd.read_excel(uploaded_file, parse_dates=["week"])
            st.session_state.exceptions = compute_exceptions(st.session_state.df)
            st.session_state.ai_outputs = {}
            st.success(f"✅ Loaded {len(st.session_state.df)} records from {uploaded_file.name}")
        except Exception as e:
            st.error(f"File error: {e}")

    # Main content
    if st.session_state.df is not None:
        df = st.session_state.df
        exceptions = st.session_state.exceptions

        # KPI Metrics
        total_skus = df["sku"].nunique()
        critical_count = sum(1 for e in exceptions if e["severity"] == "Critical")
        high_count = sum(1 for e in exceptions if e["severity"] == "High")
        total_at_risk = sum(e["at_risk_value"] for e in exceptions)
        
        hist_df = df[df["actual_qty"].notna()]
        avg_accuracy = 100 - hist_df["variance_pct"].abs().mean() if not hist_df.empty else 0

        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total SKUs Tracked</div>
                <div class="metric-value">{total_skus}</div>
                <div class="metric-delta" style="color:#8ab4d4">Active in planning cycle</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Critical Exceptions</div>
                <div class="metric-value delta-neg">{critical_count}</div>
                <div class="metric-delta delta-neg">Require immediate action</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">High Priority Alerts</div>
                <div class="metric-value delta-warn">{high_count}</div>
                <div class="metric-delta delta-warn">Action needed this week</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Inventory at Risk</div>
                <div class="metric-value delta-neg">${total_at_risk:,.0f}</div>
                <div class="metric-delta delta-neg">Below safety stock threshold</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Charts row
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown('<p class="section-header">Forecast vs Actual — Select SKU</p>', unsafe_allow_html=True)
            selected_sku = st.selectbox("", df["sku"].unique(), label_visibility="collapsed")
            st.plotly_chart(chart_forecast_vs_actual(df, selected_sku), use_container_width=True, config={"displayModeBar": False})
        
        with col2:
            st.markdown('<p class="section-header">Exception Severity Map</p>', unsafe_allow_html=True)
            heatmap = chart_exception_heatmap(exceptions)
            if heatmap:
                st.plotly_chart(heatmap, use_container_width=True, config={"displayModeBar": False})

        # Exception table
        st.markdown('<p class="section-header">Exception Queue</p>', unsafe_allow_html=True)
        
        severity_colors = {"Critical": "badge-red", "High": "badge-amber", "Medium": "badge-blue", "Low": "badge-green"}
        
        st.markdown("""
        <div class="exc-row exc-header">
            <span>SKU / Description</span>
            <span>Category</span>
            <span>Severity</span>
            <span>Weeks of Cover</span>
            <span>At Risk ($)</span>
        </div>
        """, unsafe_allow_html=True)
        
        for e in exceptions:
            badge_class = severity_colors.get(e["severity"], "badge-blue")
            issues_text = " · ".join(e["issues"][:2])
            st.markdown(f"""
            <div class="exc-row">
                <span>
                    <strong style="font-size:0.85rem">{e['sku']}</strong><br>
                    <span style="font-size:0.75rem;color:#8ab4d4">{e['description']}</span><br>
                    <span style="font-size:0.72rem;color:#4a7fa5">{issues_text}</span>
                </span>
                <span style="font-size:0.82rem;color:#8ab4d4">{e['category']}</span>
                <span><span class="badge {badge_class}">{e['severity']}</span></span>
                <span style="font-size:0.9rem;font-weight:600;color:{'#dc2626' if e['woc'] < 2 else '#d97706' if e['woc'] < 4 else '#16a34a'}">{e['woc']:.1f}w</span>
                <span style="font-size:0.85rem;font-weight:600">${e['at_risk_value']:,.0f}</span>
            </div>
            """, unsafe_allow_html=True)

        # AI Analysis
        st.markdown('<p class="section-header">AI Analysis</p>', unsafe_allow_html=True)
        
        if not st.session_state.api_key:
            st.warning("🔑 Add your Anthropic API key above to unlock AI-generated insights.")
        else:
            run_ai = st.button("🤖 Run AI Analysis", type="primary")
            
            if run_ai:
                st.session_state.ai_outputs = generate_all_outputs(df, exceptions)
            
            if st.session_state.ai_outputs:
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📋 Exception Summary",
                    "📧 Executive Email",
                    "✅ Planner Recommendations",
                    "⚠️ Risk Analysis"
                ])
                
                with tab1:
                    st.markdown(f"""
                    <div class="ai-block">
                        <div class="ai-block-title">AI Exception Analysis</div>
                        <div style="font-size:0.87rem;line-height:1.75;color:#cce0f5;white-space:pre-wrap">{st.session_state.ai_outputs.get('exception', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with tab2:
                    email_text = st.session_state.ai_outputs.get("email", "")
                    st.markdown(f"""
                    <div class="ai-block">
                        <div class="ai-block-title">Draft Executive Email</div>
                        <div class="email-output">{email_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.download_button(
                        "📥 Download Email Draft",
                        data=email_text,
                        file_name="supply_chain_exec_update.txt",
                        mime="text/plain"
                    )
                
                with tab3:
                    st.markdown(f"""
                    <div class="ai-block">
                        <div class="ai-block-title">Weekly Planner Action Plan</div>
                        <div style="font-size:0.87rem;line-height:1.75;color:#cce0f5;white-space:pre-wrap">{st.session_state.ai_outputs.get('recommendations', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with tab4:
                    risk_text = st.session_state.ai_outputs.get('risk', '')
                    severity_colors = {"CRITICAL": "#dc2626", "HIGH": "#d97706", "MEDIUM": "#2563eb", "LOW": "#16a34a"}
                    prob_colors = {"HIGH": "#fee2e2", "MEDIUM": "#fef3c7", "LOW": "#dcfce7"}
                    prob_text = {"HIGH": "#991b1b", "MEDIUM": "#92400e", "LOW": "#166534"}
                    
                    import re
                    risk_blocks = re.split(r'RISK\s+\d+\s*[-—]', risk_text)
                    risk_blocks = [b.strip() for b in risk_blocks if b.strip()]
                    
                    st.markdown('<div class="ai-block-title" style="font-size:0.75rem;font-weight:600;color:#8ab4d4;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:12px">Supply Chain Risk Register</div>', unsafe_allow_html=True)
                    
                    for idx, block in enumerate(risk_blocks):
                        lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
                        if not lines:
                            continue
                        
                        title = lines[0]
                        meta = lines[1] if len(lines) > 1 else ""
                        prob_line = lines[2] if len(lines) > 2 else ""
                        body_lines = lines[3:] if len(lines) > 3 else []
                        body = " ".join(body_lines)
                        
                        prob = "MEDIUM"
                        impact = "MEDIUM"
                        pm = re.search(r'Probability:\s*(HIGH|MEDIUM|LOW)', prob_line, re.IGNORECASE)
                        im = re.search(r'Impact:\s*(HIGH|MEDIUM|LOW)', prob_line, re.IGNORECASE)
                        if pm: prob = pm.group(1).upper()
                        if im: impact = im.group(1).upper()
                        
                        border_color = "#dc2626" if prob == "HIGH" and impact == "HIGH" else "#d97706" if prob == "HIGH" or impact == "HIGH" else "#2563eb"
                        pbg = prob_colors.get(prob, "#fef3c7")
                        ptx = prob_text.get(prob, "#92400e")
                        ibg = prob_colors.get(impact, "#fef3c7")
                        itx = prob_text.get(impact, "#92400e")
                        
                        mitigation = ""
                        analysis = ""
                        for line in body_lines:
                            if line.startswith("Mitigation:"):
                                mitigation = line.replace("Mitigation:", "").strip()
                            elif line.startswith("Analysis:"):
                                analysis = line.replace("Analysis:", "").strip()
                            elif not analysis:
                                analysis += " " + line
                        
                        st.markdown(f"""
                        <div style="background:#0d1f3c;border:1px solid #1e3a5f;border-left:3px solid {border_color};border-radius:10px;padding:1rem 1.25rem;margin-bottom:10px">
                            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                                <span style="font-size:0.7rem;font-weight:700;color:#4a7fa5">RISK {idx+1}</span>
                                <span style="font-size:0.87rem;font-weight:600;color:#ffffff">{title}</span>
                            </div>
                            <div style="font-size:0.75rem;color:#8ab4d4;margin-bottom:8px">{meta}</div>
                            <div style="display:flex;gap:8px;margin-bottom:10px">
                                <span style="background:{pbg};color:{ptx};font-size:0.68rem;font-weight:600;padding:2px 10px;border-radius:20px">Prob: {prob}</span>
                                <span style="background:{ibg};color:{itx};font-size:0.68rem;font-weight:600;padding:2px 10px;border-radius:20px">Impact: {impact}</span>
                            </div>
                            <p style="font-size:0.82rem;color:#cce0f5;line-height:1.6;margin:0 0 8px">{analysis.strip()}</p>
                            {f'<div style="background:#112244;border-radius:6px;padding:8px 12px;font-size:0.8rem;color:#2d9cdb;line-height:1.5"><strong>Mitigation:</strong> {mitigation}</div>' if mitigation else ''}
                        </div>
                        """, unsafe_allow_html=True)

        # Export
        st.markdown('<p class="section-header">Export</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button("📥 Export Forecast Data (CSV)", data=csv,
                file_name="forecast_export.csv", mime="text/csv", use_container_width=True)
        with col2:
            if exceptions:
                exc_df = pd.DataFrame([{
                    "SKU": e["sku"], "Description": e["description"],
                    "Severity": e["severity"], "Issues": " | ".join(e["issues"]),
                    "Weeks of Cover": e["woc"], "At Risk $": e["at_risk_value"]
                } for e in exceptions])
                st.download_button("📥 Export Exception Report (CSV)", data=exc_df.to_csv(index=False),
                    file_name="exception_report.csv", mime="text/csv", use_container_width=True)

    else:
        # Empty state
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#4a7fa5">
            <div style="font-size:3rem;margin-bottom:1rem">📦</div>
            <p style="font-size:1rem;font-weight:500;color:#8ab4d4">No data loaded yet</p>
            <p style="font-size:0.85rem">Click "Generate Demo Data" to see a live example,<br>or upload your own forecast file above.</p>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="kraman-footer">
        KRAMAN Corp · AI Demand Planning Copilot · Supply Chain & IT Solutions
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
