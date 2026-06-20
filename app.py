import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import anthropic
import json
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Demand Planning Copilot",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Core layout */
    .main .block-container { padding: 2rem 2.5rem 3rem; max-width: 1400px; }
    
    /* Header */
    .app-header {
        display: flex; align-items: center; gap: 16px;
        border-bottom: 1px solid #e2e8f0; padding-bottom: 1.25rem; margin-bottom: 2rem;
    }
    .app-logo {
        width: 42px; height: 42px; border-radius: 10px;
        background: #0f4c81; display: flex; align-items: center;
        justify-content: center; font-size: 20px;
    }
    .app-title { font-size: 1.3rem; font-weight: 600; color: #0f172a; margin: 0; }
    .app-subtitle { font-size: 0.8rem; color: #64748b; margin: 0; }
    .powered-badge {
        margin-left: auto; background: #f1f5f9; border: 1px solid #e2e8f0;
        border-radius: 20px; padding: 4px 12px;
        font-size: 0.7rem; color: #64748b; font-weight: 500;
    }

    /* Metric cards */
    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 2rem; }
    .metric-card {
        background: white; border: 1px solid #e2e8f0; border-radius: 12px;
        padding: 1.1rem 1.25rem;
    }
    .metric-label { font-size: 0.72rem; color: #64748b; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .metric-value { font-size: 1.7rem; font-weight: 700; color: #0f172a; line-height: 1; }
    .metric-delta { font-size: 0.75rem; margin-top: 4px; }
    .delta-neg { color: #dc2626; }
    .delta-pos { color: #16a34a; }
    .delta-warn { color: #d97706; }

    /* Status badges */
    .badge {
        display: inline-block; padding: 2px 10px; border-radius: 20px;
        font-size: 0.7rem; font-weight: 600;
    }
    .badge-red { background: #fee2e2; color: #991b1b; }
    .badge-amber { background: #fef3c7; color: #92400e; }
    .badge-green { background: #dcfce7; color: #166534; }
    .badge-blue { background: #dbeafe; color: #1e40af; }

    /* Section headers */
    .section-header {
        font-size: 0.8rem; font-weight: 600; color: #64748b;
        text-transform: uppercase; letter-spacing: 0.08em;
        margin: 2rem 0 1rem; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;
    }

    /* AI output blocks */
    .ai-block {
        background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px;
        padding: 1.5rem; margin-bottom: 1rem;
    }
    .ai-block-title {
        font-size: 0.75rem; font-weight: 600; color: #64748b;
        text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 12px;
    }

    /* Exception table */
    .exc-row {
        display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
        gap: 12px; padding: 10px 0; border-bottom: 1px solid #f1f5f9;
        align-items: center; font-size: 0.85rem;
    }
    .exc-header {
        font-size: 0.7rem; font-weight: 600; color: #94a3b8;
        text-transform: uppercase; letter-spacing: 0.05em;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px; padding: 6px 16px;
        font-size: 0.82rem; font-weight: 500;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px; font-weight: 500; font-size: 0.85rem;
    }
    .stButton > button[kind="primary"] {
        background: #0f4c81; border-color: #0f4c81;
    }

    /* File uploader */
    .stFileUploader { border: 2px dashed #e2e8f0; border-radius: 12px; padding: 1rem; }

    /* Divider */
    hr { border-color: #f1f5f9; margin: 1.5rem 0; }
    
    /* Email output */
    .email-output {
        font-family: Georgia, serif; font-size: 0.9rem; line-height: 1.7;
        color: #1e293b; white-space: pre-wrap;
    }

    /* Risk items */
    .risk-item {
        display: flex; gap: 12px; padding: 12px 0;
        border-bottom: 1px solid #f1f5f9; align-items: flex-start;
    }
    .risk-icon { font-size: 1.1rem; min-width: 24px; margin-top: 2px; }
    .risk-title { font-size: 0.87rem; font-weight: 600; color: #0f172a; }
    .risk-desc { font-size: 0.82rem; color: #64748b; margin-top: 2px; }
    
    /* KRAMAN watermark */
    .kraman-footer {
        text-align: center; padding: 2rem 0 0;
        font-size: 0.72rem; color: #cbd5e1; letter-spacing: 0.05em;
    }
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
    st.markdown("""
    <div class="app-header">
        <div class="app-logo">📦</div>
        <div>
            <p class="app-title">AI Demand Planning Copilot</p>
            <p class="app-subtitle">Industrial & High-Tech Supply Chain Intelligence</p>
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
                <div class="metric-delta" style="color:#64748b">Active in planning cycle</div>
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
                    <span style="font-size:0.75rem;color:#64748b">{e['description']}</span><br>
                    <span style="font-size:0.72rem;color:#94a3b8">{issues_text}</span>
                </span>
                <span style="font-size:0.82rem;color:#475569">{e['category']}</span>
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
                        <div style="font-size:0.87rem;line-height:1.75;color:#1e293b;white-space:pre-wrap">{st.session_state.ai_outputs.get('exception', '')}</div>
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
                        <div style="font-size:0.87rem;line-height:1.75;color:#1e293b;white-space:pre-wrap">{st.session_state.ai_outputs.get('recommendations', '')}</div>
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
                    
                    st.markdown('<div class="ai-block-title" style="font-size:0.75rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:12px">Supply Chain Risk Register</div>', unsafe_allow_html=True)
                    
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
                        <div style="background:white;border:0.5px solid var(--color-border-tertiary);border-left:3px solid {border_color};border-radius:var(--border-radius-lg);padding:1rem 1.25rem;margin-bottom:10px">
                            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                                <span style="font-size:0.7rem;font-weight:700;color:#94a3b8">RISK {idx+1}</span>
                                <span style="font-size:0.87rem;font-weight:600;color:#0f172a">{title}</span>
                            </div>
                            <div style="font-size:0.75rem;color:#64748b;margin-bottom:8px">{meta}</div>
                            <div style="display:flex;gap:8px;margin-bottom:10px">
                                <span style="background:{pbg};color:{ptx};font-size:0.68rem;font-weight:600;padding:2px 10px;border-radius:20px">Prob: {prob}</span>
                                <span style="background:{ibg};color:{itx};font-size:0.68rem;font-weight:600;padding:2px 10px;border-radius:20px">Impact: {impact}</span>
                            </div>
                            <p style="font-size:0.82rem;color:#334155;line-height:1.6;margin:0 0 8px">{analysis.strip()}</p>
                            {f'<div style="background:#f8fafc;border-radius:6px;padding:8px 12px;font-size:0.8rem;color:#0f4c81;line-height:1.5"><strong>Mitigation:</strong> {mitigation}</div>' if mitigation else ''}
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
        <div style="text-align:center;padding:4rem 2rem;color:#94a3b8">
            <div style="font-size:3rem;margin-bottom:1rem">📦</div>
            <p style="font-size:1rem;font-weight:500;color:#64748b">No data loaded yet</p>
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
