# report.py — Daily Market Report PDF Generator
import io
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER


# ── COLORS ──────────────────────────────────────────────────
BG       = colors.HexColor("#080c10")
PANEL    = colors.HexColor("#0d1219")
BORDER   = colors.HexColor("#1a2332")
ACCENT   = colors.HexColor("#4a9eff")
GREEN    = colors.HexColor("#2ecc71")
RED      = colors.HexColor("#e74c3c")
YELLOW   = colors.HexColor("#f39c12")
TEXT     = colors.HexColor("#c8d4e0")
SUBTEXT  = colors.HexColor("#4a6080")
WHITE    = colors.HexColor("#e8f0f8")


# ── STYLES ──────────────────────────────────────────────────
def make_styles():
    return {
        "title": ParagraphStyle("title",
            fontName="Helvetica-Bold", fontSize=22,
            textColor=ACCENT, leading=28, spaceAfter=2),
        "subtitle": ParagraphStyle("subtitle",
            fontName="Helvetica", fontSize=10,
            textColor=SUBTEXT, leading=14, spaceAfter=12),
        "section": ParagraphStyle("section",
            fontName="Helvetica-Bold", fontSize=8,
            textColor=SUBTEXT, leading=12, spaceAfter=6,
            spaceBefore=16, letterSpacing=2),
        "body": ParagraphStyle("body",
            fontName="Helvetica", fontSize=10,
            textColor=TEXT, leading=16, spaceAfter=4),
        "small": ParagraphStyle("small",
            fontName="Helvetica", fontSize=8,
            textColor=SUBTEXT, leading=12),
        "alert_green": ParagraphStyle("alert_green",
            fontName="Helvetica", fontSize=9,
            textColor=GREEN, leading=14),
        "alert_yellow": ParagraphStyle("alert_yellow",
            fontName="Helvetica", fontSize=9,
            textColor=YELLOW, leading=14),
        "alert_red": ParagraphStyle("alert_red",
            fontName="Helvetica", fontSize=9,
            textColor=RED, leading=14),
        "news_title": ParagraphStyle("news_title",
            fontName="Helvetica-Bold", fontSize=9,
            textColor=WHITE, leading=13, spaceAfter=2),
        "news_meta": ParagraphStyle("news_meta",
            fontName="Helvetica", fontSize=8,
            textColor=SUBTEXT, leading=11, spaceAfter=8),
    }


def fmt(val, decimals=2, suffix=""):
    if val is None or pd.isna(val): return "N/A"
    return f"{val:,.{decimals}f}{suffix}"

def delta_str(val):
    if val is None or pd.isna(val): return ""
    arrow = "+" if val >= 0 else ""
    return f"{arrow}{val:.2f}%"


# ── MAIN GENERATOR ──────────────────────────────────────────
def generate_pdf(last: pd.Series, quotes: pd.DataFrame, news: pd.DataFrame, alerts, score: int, risk_label: str) -> bytes:
    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(buf, pagesize=A4,
                leftMargin=20*mm, rightMargin=20*mm,
                topMargin=16*mm, bottomMargin=16*mm)
    styles = make_styles()
    story  = []
    today  = datetime.now().strftime("%A, %B %d %Y")
    time   = datetime.now().strftime("%H:%M EST")

    # ── HEADER ──────────────────────────────────────────────
    header_data = [[
        Paragraph("MKTTRK", styles["title"]),
        Paragraph(f"DAILY MARKET REPORT<br/>{today} · {time}", styles["subtitle"]),
    ]]
    header_table = Table(header_data, colWidths=["50%", "50%"])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN",  (1,0), (1,0),  "RIGHT"),
        ("BACKGROUND", (0,0), (-1,-1), BG),
        ("LINEBELOW", (0,0), (-1,0), 1, ACCENT),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # ── RISK SCORE ──────────────────────────────────────────
    risk_color = RED if score >= 60 else YELLOW if score >= 30 else GREEN
    risk_data = [[
        Paragraph("COMPOSITE RISK SCORE", styles["section"]),
        Paragraph(f"{score} / 100  ·  {risk_label}", ParagraphStyle("rs",
            fontName="Helvetica-Bold", fontSize=14, textColor=risk_color)),
    ]]
    risk_table = Table(risk_data, colWidths=["40%", "60%"])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), PANEL),
        ("BOX", (0,0), (-1,-1), 1, BORDER),
        ("LEFTPADDING",  (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING",   (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0), (-1,-1), 10),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 8))

    # ── MACRO METRICS ───────────────────────────────────────
    story.append(Paragraph("MACRO INDICATORS · FRED", styles["section"]))

    macro_data = [
        ["INDICATOR", "VALUE", "INDICATOR", "VALUE"],
        ["S&P 500",       fmt(last.get("SP500"), 0),         "FED FUNDS RATE",  fmt(last.get("Fed_Rate"), 2, "%")],
        ["VIX",           fmt(last.get("VIX"), 2),           "CPI YOY",         fmt(last.get("CPI_YoY"), 1, "%")],
        ["10Y TREASURY",  fmt(last.get("Bond_10Y"), 2, "%"), "CORE PCE YOY",    fmt(last.get("Core_PCE_YoY"), 1, "%")],
        ["10Y-2Y SPREAD", fmt(last.get("Curve_10_2"), 2,"%"),"UNEMPLOYMENT",    fmt(last.get("Unemployment"), 1, "%")],
        ["HY SPREAD",     fmt(last.get("HY_Spread"), 2, "%"),"GOLD $/OZ",       fmt(last.get("Gold"), 0)],
    ]

    col_w = ["25%", "25%", "25%", "25%"]
    macro_table = Table(macro_data, colWidths=col_w)
    macro_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  BORDER),
        ("BACKGROUND",    (0,1), (-1,-1), PANEL),
        ("TEXTCOLOR",     (0,0), (-1,0),  SUBTEXT),
        ("TEXTCOLOR",     (0,1), (-1,-1), TEXT),
        ("TEXTCOLOR",     (1,1), (1,-1),  WHITE),
        ("TEXTCOLOR",     (3,1), (3,-1),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  7),
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1), (-1,-1), 9),
        ("FONTNAME",      (1,1), (1,-1),  "Helvetica-Bold"),
        ("FONTNAME",      (3,1), (3,-1),  "Helvetica-Bold"),
        ("FONTSIZE",      (1,1), (1,-1),  11),
        ("FONTSIZE",      (3,1), (3,-1),  11),
        ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LETTERSPACEING",(0,0), (-1,0),  2),
    ]))
    story.append(macro_table)
    story.append(Spacer(1, 8))

    # ── LIVE QUOTES ─────────────────────────────────────────
    if not quotes.empty:
        story.append(Paragraph("LIVE QUOTES · YFINANCE", styles["section"]))
        q_data = [["TICKER", "NAME", "PRICE", "CHG $", "CHG %"]]
        for _, r in quotes.iterrows():
            chg_color = GREEN if r["Chg %"] >= 0 else RED
            q_data.append([
                r["Ticker"], r["Nom"],
                f"${r['Prix']:,.2f}",
                f"{r['Chg $']:+.2f}",
                f"{r['Chg %']:+.2f}%",
            ])
        q_table = Table(q_data, colWidths=["12%","38%","18%","16%","16%"])
        q_style = [
            ("BACKGROUND",    (0,0), (-1,0),  BORDER),
            ("BACKGROUND",    (0,1), (-1,-1), PANEL),
            ("TEXTCOLOR",     (0,0), (-1,0),  SUBTEXT),
            ("TEXTCOLOR",     (0,1), (-1,-1), TEXT),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,0),  7),
            ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",      (0,1), (-1,-1), 9),
            ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ("RIGHTPADDING",  (0,0), (-1,-1), 10),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("ALIGN",         (2,0), (-1,-1), "RIGHT"),
        ]
        for i, row in enumerate(quotes.itertuples(), start=1):
            color = GREEN if row._4 >= 0 else RED
            q_style.append(("TEXTCOLOR", (3,i), (4,i), color))
            q_style.append(("FONTNAME",  (3,i), (4,i), "Helvetica-Bold"))
        q_table.setStyle(TableStyle(q_style))
        story.append(q_table)
        story.append(Spacer(1, 8))

    # ── ALERTS ──────────────────────────────────────────────
    if alerts:
        story.append(Paragraph("RISK ALERTS", styles["section"]))
        for alert in alerts:
            style_key = "alert_" + alert.level.lower()
            prefix = "OK" if alert.level == "GREEN" else "WARN" if alert.level == "YELLOW" else "ALERT"
            story.append(Paragraph(f"[{prefix}]  {alert.message}", styles[style_key]))
        story.append(Spacer(1, 8))

    # ── NEWS ────────────────────────────────────────────────
    if not news.empty:
        story.append(Paragraph("TOP NEWS", styles["section"]))
        for i, (_, r) in enumerate(news.head(8).iterrows()):
            t = r["publishedAt"][:10] if r["publishedAt"] else ""
            story.append(Paragraph(str(r["title"]), styles["news_title"]))
            story.append(Paragraph(str(r["source"]) + "  ·  " + t, styles["news_meta"]))

    # ── FOOTER ──────────────────────────────────────────────
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Generated by MKTTRK  ·  Data: FRED, yFinance, NewsAPI  ·  " + datetime.now().strftime("%Y-%m-%d %H:%M"),
        styles["small"]
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()
