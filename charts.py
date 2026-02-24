# charts.py
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

C = {
    "bg":     "#0f1117",
    "panel":  "#1a1d2e",
    "accent": "#4f8ef7",
    "green":  "#2ecc71",
    "red":    "#e74c3c",
    "yellow": "#f39c12",
    "grey":   "#8892a4",
    "white":  "#e8eaf0",
}

_LAYOUT = dict(
    paper_bgcolor=C["bg"],
    plot_bgcolor=C["panel"],
    font=dict(color=C["white"], family="Inter, sans-serif", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(gridcolor="#2a2d3e"),
    yaxis=dict(gridcolor="#2a2d3e"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

def _apply(fig):
    fig.update_layout(**_LAYOUT)
    return fig

def chart_sp500(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["SP500"], name="S&P 500",
        line=dict(color=C["accent"], width=2), fill="tozeroy",
        fillcolor="rgba(79,142,247,0.08)"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SP500"].rolling(50).mean(), name="MA 50",
        line=dict(color=C["yellow"], width=1.2, dash="dot")))
    fig.add_trace(go.Scatter(x=df.index, y=df["SP500"].rolling(200).mean(), name="MA 200",
        line=dict(color=C["red"], width=1.2, dash="dot")))
    fig.update_layout(title="S&P 500 avec Moyennes Mobiles")
    return _apply(fig)

def chart_rates(df):
    series_map = {
        "Bond_2Y":  ("2Y Treasury",  C["green"]),
        "Bond_10Y": ("10Y Treasury", C["accent"]),
        "Bond_30Y": ("30Y Treasury", C["yellow"]),
        "Fed_Rate": ("Fed Rate",     C["red"]),
    }
    fig = go.Figure()
    for col, (name, color) in series_map.items():
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=name,
                line=dict(color=color, width=1.8)))
    fig.update_layout(title="Taux d'intérêt", yaxis_title="%")
    return _apply(fig)

def chart_curve(df):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.5, 0.5], vertical_spacing=0.08)
    for row, col, name in [(1, "Curve_10_2", "10Y-2Y"), (2, "Curve_10_3m", "10Y-3M")]:
        if col not in df.columns: continue
        s = df[col]
        colors = [C["green"] if v >= 0 else C["red"] for v in s]
        fig.add_trace(go.Bar(x=df.index, y=s, name=name, marker_color=colors), row=row, col=1)
        fig.add_hline(y=0, line_color="white", line_width=0.8, line_dash="dot", row=row, col=1)
    fig.update_layout(title="Courbe des taux")
    fig.update_layout(**_LAYOUT)
    return fig

def chart_vix(df):
    fig = go.Figure()
    if "VIX" not in df.columns: return fig
    fig.add_hrect(y0=0,  y1=15,  fillcolor=C["green"],  opacity=0.07, line_width=0)
    fig.add_hrect(y0=15, y1=25,  fillcolor=C["yellow"], opacity=0.07, line_width=0)
    fig.add_hrect(y0=25, y1=100, fillcolor=C["red"],    opacity=0.07, line_width=0)
    fig.add_trace(go.Scatter(x=df.index, y=df["VIX"], name="VIX",
        line=dict(color=C["white"], width=1.8),
        fill="tozeroy", fillcolor="rgba(232,234,240,0.06)"))
    fig.add_hline(y=15, line_color=C["green"], line_dash="dash",
                  annotation_text="Calme", annotation_position="top right")
    fig.add_hline(y=25, line_color=C["red"], line_dash="dash",
                  annotation_text="Stress", annotation_position="top right")
    fig.update_layout(title="VIX — Indice de Volatilité")
    return _apply(fig)

def chart_inflation(df):
    fig = go.Figure()
    for col, name, color in [
        ("CPI_YoY",      "CPI YoY %",      C["red"]),
        ("Core_PCE_YoY", "Core PCE YoY %", C["accent"]),
    ]:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=name,
                line=dict(color=color, width=2)))
    fig.add_hline(y=2.0, line_color=C["green"], line_dash="dot",
                  annotation_text="Cible Fed 2%", annotation_position="bottom right")
    fig.update_layout(title="Inflation — CPI & Core PCE (YoY %)", yaxis_title="%")
    return _apply(fig)

def chart_credit(df):
    fig = go.Figure()
    for col, name, color in [
        ("HY_Spread", "High Yield Spread", C["red"]),
        ("IG_Spread", "IG Spread",         C["accent"]),
    ]:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=name,
                line=dict(color=color, width=2)))
    fig.update_layout(title="Spreads de Crédit", yaxis_title="%")
    return _apply(fig)

def chart_commodities(df):
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("WTI Oil ($/bbl)", "Gold ($/oz)"))
    for col, rc, color in [("Oil_WTI", (1,1), C["yellow"]), ("Gold", (1,2), C["accent"])]:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col],
                line=dict(color=color, width=1.8), showlegend=False), row=rc[0], col=rc[1])
    fig.update_layout(title="Matières Premières")
    fig.update_layout(**_LAYOUT)
    return fig

def chart_correlation(df):
    fig = go.Figure()
    if "Stock_Bond_Corr" not in df.columns: return fig
    s = df["Stock_Bond_Corr"]
    colors = [C["green"] if v < 0 else C["red"] for v in s]
    fig.add_trace(go.Bar(x=df.index, y=s, marker_color=colors, name="Corr 30J"))
    fig.add_hline(y=0, line_color="white", line_width=0.8, line_dash="dot")
    fig.update_layout(title="Corrélation Actions-Obligations (30J)",
                      yaxis=dict(range=[-1, 1]))
    return _apply(fig)

def chart_unemployment(df):
    fig = go.Figure()
    if "Unemployment" not in df.columns: return fig
    fig.add_trace(go.Scatter(x=df.index, y=df["Unemployment"], name="Chômage",
        line=dict(color=C["yellow"], width=2),
        fill="tozeroy", fillcolor="rgba(243,156,18,0.08)"))
    fig.update_layout(title="Taux de Chômage (%)", yaxis_title="%")
    return _apply(fig)