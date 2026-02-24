# alerts.py
from dataclasses import dataclass
from typing import Literal
import pandas as pd
from config import ALERTS

Level = Literal["GREEN", "YELLOW", "RED"]

LEVEL_EMOJI = {"GREEN": "OK", "YELLOW": "WARN", "RED": "ALERT"}
LEVEL_COLOR = {"GREEN": "#2ecc71", "YELLOW": "#f39c12", "RED": "#e74c3c"}


@dataclass
class Alert:
    key: str
    label: str
    value: float
    level: Level
    message: str


class AlertEngine:
    def __init__(self, last: pd.Series):
        self.last = last
        self.alerts: list[Alert] = []
        self._evaluate()

    def risk_score(self) -> int:
        score = 0
        for a in self.alerts:
            if a.level == "RED":
                score += 25
            elif a.level == "YELLOW":
                score += 10
        return min(score, 100)

    def risk_label(self) -> tuple[str, str]:
        s = self.risk_score()
        if s >= 60:
            return "HIGH RISK", LEVEL_COLOR["RED"]
        if s >= 30:
            return "ELEVATED RISK", LEVEL_COLOR["YELLOW"]
        return "LOW RISK", LEVEL_COLOR["GREEN"]

    def _evaluate(self):
        self._check_vix(self.last)
        self._check_curves(self.last)
        self._check_hy_spread(self.last)
        self._check_cpi(self.last)
        self._check_sp500(self.last)

    def _add(self, key, label, value, level, message):
        self.alerts.append(Alert(key, label, value, level, message))

    def _check_vix(self, last):
        if "VIX" not in last or pd.isna(last["VIX"]):
            return
        v = last["VIX"]
        cfg = ALERTS["VIX"]
        if v > cfg["high"]:
            self._add("VIX", cfg["label"], v, "RED", "VIX a " + str(round(v, 1)) + " - marches stresses (>25)")
        elif v > cfg["low"]:
            self._add("VIX", cfg["label"], v, "YELLOW", "VIX a " + str(round(v, 1)) + " - volatilite moderee (15-25)")
        else:
            self._add("VIX", cfg["label"], v, "GREEN", "VIX a " + str(round(v, 1)) + " - marches calmes (<15)")

    def _check_curves(self, last):
        for key in ["Curve_10_2", "Curve_10_3m"]:
            if key not in last or pd.isna(last[key]):
                continue
            v = last[key]
            cfg = ALERTS[key]
            if v < cfg["inversion"]:
                self._add(key, cfg["label"], v, "RED", cfg["label"] + " inversee a " + str(round(v, 2)) + "% - risque recession")
            elif v < 0.25:
                self._add(key, cfg["label"], v, "YELLOW", cfg["label"] + " quasi-plate a " + str(round(v, 2)) + "%")
            else:
                self._add(key, cfg["label"], v, "GREEN", cfg["label"] + " normale a " + str(round(v, 2)) + "%")

    def _check_hy_spread(self, last):
        if "HY_Spread" not in last or pd.isna(last["HY_Spread"]):
            return
        v = last["HY_Spread"]
        cfg = ALERTS["HY_Spread"]
        if v > cfg["high"] / 100:
            self._add("HY_Spread", cfg["label"], v, "RED", "HY Spread a " + str(round(v, 2)) + "% - stress credit eleve")
        elif v > cfg["low"] / 100:
            self._add("HY_Spread", cfg["label"], v, "YELLOW", "HY Spread a " + str(round(v, 2)) + "% - credit moderement large")
        else:
            self._add("HY_Spread", cfg["label"], v, "GREEN", "HY Spread a " + str(round(v, 2)) + "% - credit sain")

    def _check_cpi(self, last):
        if "CPI_YoY" not in last or pd.isna(last["CPI_YoY"]):
            return
        v = last["CPI_YoY"]
        if v > 4.0:
            self._add("CPI", "CPI YoY", v, "RED", "CPI a " + str(round(v, 1)) + "% - inflation bien au-dessus de la cible")
        elif v > 2.5:
            self._add("CPI", "CPI YoY", v, "YELLOW", "CPI a " + str(round(v, 1)) + "% - inflation legerement au-dessus")
        else:
            self._add("CPI", "CPI YoY", v, "GREEN", "CPI a " + str(round(v, 1)) + "% - inflation proche de la cible")

    def _check_sp500(self, last):
        if "SP500_20D_Ret" not in last or pd.isna(last["SP500_20D_Ret"]):
            return
        v = last["SP500_20D_Ret"]
        if v < -10:
            self._add("SP500", "S&P 500 (20J)", v, "RED", "S&P 500 en baisse de " + str(round(v, 1)) + "% sur 20j - forte correction")
        elif v < -5:
            self._add("SP500", "S&P 500 (20J)", v, "YELLOW", "S&P 500 en baisse de " + str(round(v, 1)) + "% sur 20j - correction moderee")
        else:
            self._add("SP500", "S&P 500 (20J)", v, "GREEN", "S&P 500 a " + str(round(v, 1)) + "% sur 20j - stable")
