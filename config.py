# config.py
FRED_API_KEY = "6d303a5fbeeaf62a17b506f3b109f2a1"
NEWS_API_KEY = "a0f0329c7e9b412a8d222126da0552c9"
START_DATE = "2022-01-01"

SERIES = {
    "SP500":        {"id": "SP500",        "label": "S&P 500",            "category": "Equity"},
    "VIX":          {"id": "VIXCLS",       "label": "VIX",                "category": "Equity"},
    "Bond_2Y":      {"id": "DGS2",         "label": "2Y Treasury (%)",    "category": "Rates"},
    "Bond_10Y":     {"id": "DGS10",        "label": "10Y Treasury (%)",   "category": "Rates"},
    "Bond_30Y":     {"id": "DGS30",        "label": "30Y Treasury (%)",   "category": "Rates"},
    "Fed_Rate":     {"id": "FEDFUNDS",     "label": "Fed Funds Rate (%)", "category": "Rates"},
    "Curve_10_2":   {"id": "T10Y2Y",       "label": "10Y-2Y Spread",      "category": "Curve"},
    "Curve_10_3m":  {"id": "T10Y3M",       "label": "10Y-3M Spread",      "category": "Curve"},
    "CPI":          {"id": "CPIAUCSL",     "label": "CPI (YoY %)",        "category": "Macro"},
    "Core_PCE":     {"id": "PCEPILFE",     "label": "Core PCE (YoY %)",   "category": "Macro"},
    "Unemployment": {"id": "UNRATE",       "label": "Unemployment (%)",   "category": "Macro"},
    "HY_Spread":    {"id": "BAMLH0A0HYM2", "label": "HY Credit Spread",  "category": "Credit"},
    "IG_Spread":    {"id": "BAMLC0A0CM",   "label": "IG Credit Spread",   "category": "Credit"},
    "DXY":          {"id": "DTWEXBGS",     "label": "USD Index (DXY)",    "category": "FX"},
    "Oil_WTI":      {"id": "DCOILWTICO",   "label": "Oil WTI ($/bbl)",    "category": "Commodities"},
    "Gold":         {"id": "GOLD",         "label": "Gold ($/oz)",        "category": "Commodities"},
}

# yfinance tickers
YFINANCE_TICKERS = {
    "SPY":  "S&P 500 ETF",
    "QQQ":  "Nasdaq 100 ETF",
    "GLD":  "Gold ETF",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "GOOGL":"Alphabet",
    "AMZN": "Amazon",
    "META": "Meta",
    "TSLA": "Tesla",
}

ALERTS = {
    "VIX":         {"high": 25,  "low": 15,  "label": "VIX"},
    "Curve_10_2":  {"inversion": 0,           "label": "10Y-2Y Curve"},
    "Curve_10_3m": {"inversion": 0,           "label": "10Y-3M Curve"},
    "HY_Spread":   {"high": 500, "low": 300,  "label": "HY Spread (bps)"},
}

ROLLING_CORR_WINDOW = 30
ROLLING_RETURN_WINDOW = 20
