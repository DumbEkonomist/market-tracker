# data.py
import pandas as pd
from fredapi import Fred
from config import FRED_API_KEY, SERIES, START_DATE, ROLLING_CORR_WINDOW


class MarketData:
    def __init__(self):
        self.fred = Fred(api_key=FRED_API_KEY)
        self.raw = pd.DataFrame()
        self.df = pd.DataFrame()

    def load(self):
        self._fetch()
        self._clean()
        self._enrich()
        return self.df

    def last_values(self):
        return self.df.iloc[-1]

    def _fetch(self):
        frames = {}
        errors = []
        for key, meta in SERIES.items():
            try:
                frames[key] = self.fred.get_series(meta["id"], observation_start=START_DATE)
            except Exception as e:
                errors.append(str(key) + ": " + str(e))
        if errors:
            print("[WARN] Could not fetch: " + ", ".join(errors))
        self.raw = pd.DataFrame(frames)

    def _clean(self):
        df = self.raw.copy()
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.ffill()
        df = df.dropna(subset=["SP500"])
        self.df = df

    def _enrich(self):
        df = self.df
        if "SP500" in df.columns:
            df["SP500_1D_Ret"] = df["SP500"].pct_change() * 100
            df["SP500_20D_Ret"] = df["SP500"].pct_change(20) * 100
        for col in ["CPI", "Core_PCE"]:
            if col in df.columns:
                df[col + "_YoY"] = df[col].pct_change(252) * 100
        if "SP500" in df.columns and "Bond_10Y" in df.columns:
            sp_ret = df["SP500"].pct_change()
            bond_chg = df["Bond_10Y"].diff()
            df["Stock_Bond_Corr"] = sp_ret.rolling(30).corr(bond_chg)
        if "Bond_10Y" in df.columns and "Fed_Rate" in df.columns:
            df["Rate_Gap"] = df["Bond_10Y"] - df["Fed_Rate"]
        self.df = df
