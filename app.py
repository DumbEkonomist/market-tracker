# app.py — Market Tracker | Bloomberg-core UI
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

from data   import MarketData
from alerts import AlertEngine, LEVEL_COLOR, LEVEL_EMOJI
from live   import LiveData
from report import generate_pdf
from charts import (
    chart_sp500, chart_rates, chart_curve, chart_vix,
    chart_inflation, chart_credit, chart_commodities,
    chart_correlation, chart_unemployment,
)

st.set_page_config(page_title="MKTTRK", page_icon="*", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    font-family: 'IBM Plex Mono', monospace !important;
    background: #080c10 !important;
    color: #c8d4e0 !important;
}
#MainMenu, footer, header, .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── TOPBAR ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 24px; height: 48px; background: #080c10;
    border-bottom: 1px solid #1a2332;
}
.topbar-logo   { font-size: 13px; font-weight: 600; color: #4a9eff; letter-spacing: 0.2em; }
.topbar-right  { display: flex; align-items: center; gap: 16px; }
.topbar-time   { font-size: 10px; color: #4a6080; }
.topbar-status { display: flex; align-items: center; gap: 5px; font-size: 10px; color: #2ecc71; }
.topbar-dot    { width: 5px; height: 5px; background: #2ecc71; border-radius: 50%; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── CONTROL BAR BUTTONS ── */
div[data-testid="stButton"] button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 10px !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    padding: 3px 10px !important;
    border-radius: 3px !important;
    border: 1px solid #1a2332 !important;
    background: #0d1219 !important;
    color: #4a6080 !important;
    transition: all 0.15s !important;
    white-space: nowrap !important;
    height: 28px !important;
    min-height: 28px !important;
    line-height: 1 !important;
}
div[data-testid="stButton"] button:hover {
    color: #c8d4e0 !important;
    border-color: #2a3f5f !important;
    background: #111820 !important;
}

/* ── TICKER ── */
.ticker-wrapper {
    background: #0a0f18; border-bottom: 1px solid #1a2332;
    height: 36px; overflow: hidden;
}
.ticker-track {
    display: flex; align-items: center; height: 36px;
    white-space: nowrap; animation: scroll 45s linear infinite;
}
.ticker-track:hover { animation-play-state: paused; }
@keyframes scroll { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
.ticker-item { display:inline-flex; align-items:center; gap:8px; padding:0 24px; font-size:11px; border-right:1px solid #1a2332; }
.ticker-sym  { color:#4a9eff; font-weight:600; font-size:10px; }
.ticker-px   { color:#c8d4e0; }
.t-up   { color:#2ecc71; font-size:10px; }
.t-down { color:#e74c3c; font-size:10px; }

/* ── SECTIONS ── */
.sec-header {
    display: flex; align-items: center; gap: 12px;
    padding: 18px 24px 8px 24px; font-size: 9px; font-weight: 600;
    color: #4a6080; letter-spacing: 0.2em; text-transform: uppercase;
    border-top: 1px solid #1a2332; margin-top: 4px;
}
.sec-header::after { content:''; flex:1; height:1px; background:#1a2332; }

/* ── METRICS ── */
.metric-card {
    background: #0d1219; border: 1px solid #1a2332;
    border-radius: 3px; padding: 14px 18px; transition: border-color 0.15s;
}
.metric-card:hover { background: #0f1620; border-color: #2a3f5f; }
.m-label { font-size: 8px; font-weight: 600; color: #4a6080; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 8px; }
.m-value { font-size: 20px; font-weight: 600; color: #e8f0f8; line-height: 1; margin-bottom: 5px; }
.m-up   { font-size: 10px; color: #2ecc71; }
.m-down { font-size: 10px; color: #e74c3c; }

/* ── ALERTS ── */
.alert-card {
    padding: 10px 14px; border-radius: 3px; border-left: 2px solid;
    background: #0d1219; display: flex; align-items: center;
    justify-content: space-between; font-size: 10px;
}
.alert-badge { font-size: 8px; font-weight: 700; letter-spacing: 0.1em; padding: 2px 7px; border-radius: 2px; }

/* ── NOTE ── */
.note-display {
    margin: 8px 24px; padding: 10px 16px;
    border-left: 2px solid #4a9eff; background: #0d1828;
    border-radius: 0 3px 3px 0; font-size: 11px; color: #c8d4e0; line-height: 1.6;
}
.note-label { font-size: 8px; color: #4a9eff; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 4px; }

div[data-testid="stTextInput"] input {
    background: #0a0f18 !important; color: #c8d4e0 !important;
    border: none !important; border-bottom: 1px solid #1a2332 !important;
    border-radius: 0 !important; font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important; padding: 8px 24px !important;
    box-shadow: none !important;
}

/* ── NEWS ── */
.news-item {
    background: #0d1219; border: 1px solid #1a2332;
    border-radius: 3px; padding: 12px 14px; margin-bottom: 6px;
}
.news-item:hover { border-color: #2a3f5f; }
.news-meta { font-size: 8px; color: #4a6080; margin-bottom: 5px; }
.news-src  { color: #4a9eff; }
.news-hl   { font-size: 11px; color: #c8d4e0; line-height: 1.5; }
.news-hl a { color: #c8d4e0; text-decoration: none; }
.news-hl a:hover { color: #4a9eff; }

.chart-wrap { padding: 0 24px; }
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: #080c10; }
::-webkit-scrollbar-thumb { background: #1a2332; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE ────────────────────────────────────────────
if "lookback"     not in st.session_state: st.session_state.lookback     = "1Y"
if "show_quotes"  not in st.session_state: st.session_state.show_quotes  = True
if "show_news"    not in st.session_state: st.session_state.show_news    = True
if "show_charts"  not in st.session_state: st.session_state.show_charts  = True


# ── CACHE ───────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def load_fred_data():
    return MarketData().load()

@st.cache_data(ttl=300, show_spinner=False)
def load_quotes():
    return LiveData().get_quotes()

@st.cache_data(ttl=600, show_spinner=False)
def load_news():
    return LiveData().get_news(query="stock market economy federal reserve", page_size=12)

@st.cache_data(ttl=300, show_spinner=False)
def load_history(ticker, period):
    return LiveData().get_history(ticker, period)

def fmt(val, decimals=2, suffix=""):
    if val is None or pd.isna(val): return "N/A"
    return f"{val:,.{decimals}f}{suffix}"

CHART_STYLE = dict(
    paper_bgcolor="#080c10", plot_bgcolor="#0d1219",
    font=dict(color="#c8d4e0", family="IBM Plex Mono", size=11),
    xaxis=dict(gridcolor="#1a2332"), yaxis=dict(gridcolor="#1a2332"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=10, r=10, t=36, b=10),
)
def apply_style(fig):
    fig.update_layout(**CHART_STYLE)
    return fig


# ── LOAD DATA ────────────────────────────────────────────────
with st.spinner(""):
    df_full = load_fred_data()
with st.spinner(""):
    quotes = load_quotes()

days_map = {"6M":180,"1Y":365,"2Y":730,"3Y":1095,"ALL":9999}
cutoff   = pd.Timestamp.today() - pd.Timedelta(days=days_map[st.session_state.lookback])
df       = df_full[df_full.index >= cutoff].copy()
last     = df.iloc[-1]
engine   = AlertEngine(last)
score    = engine.risk_score()
risk_label, risk_color = engine.risk_label()
now_str  = datetime.now().strftime("%Y-%m-%d  %H:%M")


# ── TOPBAR ───────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
  <div class="topbar-logo">MKTTRK</div>
  <div class="topbar-right">
    <div class="topbar-time">{now_str}</div>
    <div class="topbar-status"><div class="topbar-dot"></div>LIVE</div>
  </div>
</div>""", unsafe_allow_html=True)


# ── CONTROL BAR ──────────────────────────────────────────────
cb = st.columns([0.4, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 1, 1, 2])
with cb[0]: st.markdown("<div style='font-size:9px;color:#4a6080;padding-top:7px;padding-left:8px'>PERIOD</div>", unsafe_allow_html=True)
with cb[1]:
    if st.button("6M"):  st.session_state.lookback = "6M";  st.rerun()
with cb[2]:
    if st.button("1Y"):  st.session_state.lookback = "1Y";  st.rerun()
with cb[3]:
    if st.button("2Y"):  st.session_state.lookback = "2Y";  st.rerun()
with cb[4]:
    if st.button("3Y"):  st.session_state.lookback = "3Y";  st.rerun()
with cb[5]:
    if st.button("ALL"): st.session_state.lookback = "ALL"; st.rerun()
with cb[6]:
    lbl = "QUOTES ON" if st.session_state.show_quotes else "QUOTES OFF"
    if st.button(lbl): st.session_state.show_quotes = not st.session_state.show_quotes; st.rerun()
with cb[7]:
    lbl = "NEWS ON" if st.session_state.show_news else "NEWS OFF"
    if st.button(lbl): st.session_state.show_news = not st.session_state.show_news; st.rerun()
with cb[8]:
    lbl = "CHARTS ON" if st.session_state.show_charts else "CHARTS OFF"
    if st.button(lbl): st.session_state.show_charts = not st.session_state.show_charts; st.rerun()
with cb[9]:
    if st.button("REFRESH DATA"): st.cache_data.clear(); st.rerun()


# ── SCROLLING TICKER ─────────────────────────────────────────
if not quotes.empty:
    items = ""
    for _, r in quotes.iterrows():
        cls   = "t-up" if r["Chg %"] >= 0 else "t-down"
        arrow = "+" if r["Chg %"] >= 0 else ""
        items += f'<div class="ticker-item"><span class="ticker-sym">{r["Ticker"]}</span><span class="ticker-px">${r["Prix"]:,.2f}</span><span class="{cls}">{arrow}{r["Chg %"]:.2f}%</span></div>'
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-track">{items+items}</div></div>', unsafe_allow_html=True)


# ── NOTE DU TRADER ───────────────────────────────────────────
note = st.text_input("", placeholder="Note du jour — ex: FOMC jeudi, surveille NVDA...", label_visibility="collapsed")
if note.strip():
    st.markdown(f"""
    <div class="note-display">
      <div class="note-label">NOTE DU TRADER · {datetime.now().strftime('%b %d, %Y')}</div>
      {note}
    </div>""", unsafe_allow_html=True)


# ── RISK BANNER ──────────────────────────────────────────────
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div style="margin:0 24px 12px 24px;padding:14px 20px;border-radius:3px;
     border:1px solid {risk_color};background:{risk_color}10;
     display:flex;align-items:center;justify-content:space-between">
  <div>
    <div style="font-size:8px;color:{risk_color};letter-spacing:.2em;font-weight:700;margin-bottom:3px">COMPOSITE RISK SCORE</div>
    <div style="font-size:10px;color:#4a6080">{st.session_state.lookback} · FRED · {df.index[-1].strftime('%b %d, %Y')}</div>
  </div>
  <div style="display:flex;align-items:center;gap:16px">
    <div style="text-align:right">
      <div style="font-size:38px;font-weight:700;color:{risk_color};line-height:1">{score}</div>
      <div style="font-size:10px;color:{risk_color};letter-spacing:.1em">{risk_label}</div>
    </div>
    <div style="width:100px;background:#1a2332;border-radius:2px;height:4px">
      <div style="width:{score}%;background:{risk_color};height:4px;border-radius:2px"></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


# ── MACRO METRICS ────────────────────────────────────────────
st.markdown('<div class="sec-header">MACRO · FRED</div>', unsafe_allow_html=True)
for row_data in [
    [("S&P 500", fmt(last.get("SP500"),0), last.get("SP500_1D_Ret")),
     ("VIX", fmt(last.get("VIX"),2), None),
     ("10Y TREASURY", fmt(last.get("Bond_10Y"),2,"%"), None),
     ("10Y-2Y SPREAD", fmt(last.get("Curve_10_2"),2,"%"), None),
     ("FED FUNDS RATE", fmt(last.get("Fed_Rate"),2,"%"), None)],
    [("CPI YOY", fmt(last.get("CPI_YoY"),1,"%"), None),
     ("CORE PCE YOY", fmt(last.get("Core_PCE_YoY"),1,"%"), None),
     ("UNEMPLOYMENT", fmt(last.get("Unemployment"),1,"%"), None),
     ("HY SPREAD", fmt(last.get("HY_Spread"),2,"%"), None),
     ("GOLD $/OZ", fmt(last.get("Gold"),0), None)],
]:
    cols = st.columns(5)
    for i, (label, value, delta) in enumerate(row_data):
        with cols[i]:
            dh = ""
            if delta is not None and not pd.isna(delta):
                arrow = "+" if delta >= 0 else ""
                cls   = "m-up" if delta >= 0 else "m-down"
                dh = f'<div class="{cls}">{arrow}{delta:.2f}%</div>'
            st.markdown(f'<div class="metric-card"><div class="m-label">{label}</div><div class="m-value">{value}</div>{dh}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)


# ── ALERTS ───────────────────────────────────────────────────
if engine.alerts:
    st.markdown('<div class="sec-header">RISK ALERTS</div>', unsafe_allow_html=True)
    cols = st.columns(len(engine.alerts))
    for i, alert in enumerate(engine.alerts):
        c = LEVEL_COLOR[alert.level]
        with cols[i]:
            st.markdown(f'<div class="alert-card" style="border-left-color:{c}"><span style="color:#c8d4e0">{alert.message}</span><span class="alert-badge" style="background:{c}18;color:{c}">{alert.level}</span></div>', unsafe_allow_html=True)


# ── LIVE QUOTES ──────────────────────────────────────────────
if st.session_state.show_quotes and not quotes.empty:
    st.markdown('<div class="sec-header">LIVE QUOTES</div>', unsafe_allow_html=True)
    st.markdown("<div style='padding:0 24px'>", unsafe_allow_html=True)
    c1, c2 = st.columns([1,2])
    with c1:
        selected = st.selectbox("", quotes["Ticker"].tolist(), label_visibility="collapsed")
        period   = st.radio("", ["1mo","3mo","6mo","1y","2y"], horizontal=True, index=3, label_visibility="collapsed")
    with c2:
        row   = quotes[quotes["Ticker"] == selected].iloc[0]
        color = "#2ecc71" if row["Chg %"] >= 0 else "#e74c3c"
        arrow = "+" if row["Chg %"] >= 0 else ""
        st.markdown(f'<div style="padding:6px 0"><span style="font-size:26px;font-weight:700;color:#e8f0f8">${row["Prix"]:,.2f}</span>&nbsp;&nbsp;<span style="font-size:14px;color:{color}">{arrow}{row["Chg %"]:.2f}% ({row["Chg $"]:+.2f})</span>&nbsp;&nbsp;<span style="font-size:10px;color:#4a6080">{selected} · {row["Nom"]}</span></div>', unsafe_allow_html=True)
    hist = load_history(selected, period)
    if not hist.empty:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist.index, open=hist["Open"], high=hist["High"], low=hist["Low"], close=hist["Close"], name=selected, increasing_line_color="#2ecc71", decreasing_line_color="#e74c3c"))
        fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"].rolling(20).mean(), name="MA20", line=dict(color="#f39c12", width=1, dash="dot")))
        fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"].rolling(50).mean(), name="MA50", line=dict(color="#4a9eff", width=1, dash="dot")))
        fig.update_layout(paper_bgcolor="#080c10", plot_bgcolor="#0d1219", font=dict(color="#c8d4e0", family="IBM Plex Mono", size=11), xaxis=dict(gridcolor="#1a2332", rangeslider_visible=False), yaxis=dict(gridcolor="#1a2332"), legend=dict(bgcolor="rgba(0,0,0,0)"), margin=dict(l=10,r=10,t=20,b=10), height=360)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── NEWS ─────────────────────────────────────────────────────
if st.session_state.show_news:
    st.markdown('<div class="sec-header">NEWS FEED</div>', unsafe_allow_html=True)
    with st.spinner(""):
        news = load_news()
    if not news.empty:
        cols = st.columns(2)
        for i, (_, r) in enumerate(news.iterrows()):
            t = r["publishedAt"][:10] if r["publishedAt"] else ""
            with cols[i % 2]:
                st.markdown(f'<div class="news-item"><div class="news-meta"><span class="news-src">{r["source"]}</span> · {t}</div><div class="news-hl"><a href="{r["url"]}" target="_blank">{r["title"]}</a></div></div>', unsafe_allow_html=True)


# ── FRED CHARTS ──────────────────────────────────────────────
if st.session_state.show_charts:
    for section, key in [
        ("EQUITY & VOLATILITY","equity"), ("INTEREST RATES","rates"),
        ("YIELD CURVE","curve"), ("INFLATION & MACRO","macro"),
        ("CREDIT MARKETS","credit"), ("COMMODITIES","commo"),
        ("STOCK-BOND CORRELATION","corr"),
    ]:
        st.markdown(f'<div class="sec-header">{section}</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        if key == "equity":
            c1,c2 = st.columns([2,1])
            with c1: st.plotly_chart(apply_style(chart_sp500(df)), use_container_width=True)
            with c2: st.plotly_chart(apply_style(chart_vix(df)),   use_container_width=True)
        elif key == "rates":  st.plotly_chart(apply_style(chart_rates(df)),       use_container_width=True)
        elif key == "curve":  st.plotly_chart(apply_style(chart_curve(df)),       use_container_width=True)
        elif key == "macro":
            c1,c2 = st.columns(2)
            with c1: st.plotly_chart(apply_style(chart_inflation(df)),    use_container_width=True)
            with c2: st.plotly_chart(apply_style(chart_unemployment(df)), use_container_width=True)
        elif key == "credit": st.plotly_chart(apply_style(chart_credit(df)),      use_container_width=True)
        elif key == "commo":  st.plotly_chart(apply_style(chart_commodities(df)), use_container_width=True)
        elif key == "corr":   st.plotly_chart(apply_style(chart_correlation(df)), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── DAILY REPORT ─────────────────────────────────────────────
st.markdown('<div class="sec-header">DAILY REPORT</div>', unsafe_allow_html=True)
st.markdown("<div style='padding:0 24px'>", unsafe_allow_html=True)
if st.button("Generate PDF Report"):
    with st.spinner("Generating..."):
        pdf_bytes = generate_pdf(last, quotes, load_news(), engine.alerts, score, risk_label)
    st.download_button("Download PDF", data=pdf_bytes,
        file_name="mkttrk_" + datetime.now().strftime("%Y%m%d") + ".pdf",
        mime="application/pdf")
st.markdown("</div>", unsafe_allow_html=True)


# ── RAW DATA ─────────────────────────────────────────────────
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
with st.expander("RAW DATA"):
    display_cols = [c for c in ["SP500","VIX","Bond_2Y","Bond_10Y","Fed_Rate","Curve_10_2","Curve_10_3m","CPI_YoY","Core_PCE_YoY","Unemployment","HY_Spread","Oil_WTI","Gold","Stock_Bond_Corr"] if c in df.columns]
    st.dataframe(df[display_cols].tail(30).style.format("{:.2f}"), use_container_width=True)
    st.download_button("Export CSV", df[display_cols].to_csv(), "mkttrk_" + datetime.now().strftime("%Y%m%d") + ".csv", "text/csv")

st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
