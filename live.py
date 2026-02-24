# live.py
import yfinance as yf
import pandas as pd
from newsapi import NewsApiClient
from config import YFINANCE_TICKERS, NEWS_API_KEY


class LiveData:
    def __init__(self):
        self.newsapi = NewsApiClient(api_key=NEWS_API_KEY)

    # ── YFINANCE ────────────────────────────────────────────
    def get_quotes(self):
        rows = []
        for ticker, label in YFINANCE_TICKERS.items():
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="5d")
                if hist.empty:
                    continue
                last_close = hist["Close"].iloc[-1]
                prev_close = hist["Close"].iloc[-2]
                change     = last_close - prev_close
                change_pct = (change / prev_close) * 100
                rows.append({
                    "Ticker":  ticker,
                    "Nom":     label,
                    "Prix":    round(last_close, 2),
                    "Chg $":   round(change, 2),
                    "Chg %":   round(change_pct, 2),
                })
            except Exception as e:
                print("Error fetching " + ticker + ": " + str(e))
        return pd.DataFrame(rows)

    def get_history(self, ticker, period="1y"):
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period=period)
            return hist
        except Exception as e:
            print("Error fetching history for " + ticker + ": " + str(e))
            return pd.DataFrame()

    # ── NEWSAPI ─────────────────────────────────────────────
    def get_news(self, query="stock market finance economy", page_size=10):
        try:
            response = self.newsapi.get_everything(
                q=query,
                language="en",
                sort_by="publishedAt",
                page_size=page_size,
            )
            articles = response.get("articles", [])
            rows = []
            for a in articles:
                rows.append({
                    "title":       a.get("title", ""),
                    "source":      a.get("source", {}).get("name", ""),
                    "url":         a.get("url", ""),
                    "publishedAt": a.get("publishedAt", ""),
                    "description": a.get("description", ""),
                })
            return pd.DataFrame(rows)
        except Exception as e:
            print("Error fetching news: " + str(e))
            return pd.DataFrame()
