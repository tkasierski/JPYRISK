from __future__ import annotations

import math

import numpy as np
import pandas as pd

from jpy_risk.config import CONFIG


def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None


def percentile_of_last(history_series):
    """Percentile rank of last value within the provided history series."""
    s = pd.Series(history_series).dropna()
    if len(s) < 20:
        return np.nan
    last = s.iloc[-1]
    return (s <= last).mean()


def classify_percentile(p, direction="higher_is_risk"):
    """Classify a percentile value as GREEN, AMBER, RED, or GRAY."""
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "GRAY"

    amber = CONFIG["percentile_thresholds"]["amber"]
    red = CONFIG["percentile_thresholds"]["red"]

    if direction == "higher_is_risk":
        if p >= red:
            return "RED"
        if p >= amber:
            return "AMBER"
        return "GREEN"

    if direction == "lower_is_risk":
        low_red = 1 - red
        low_amber = 1 - amber
        if p <= low_red:
            return "RED"
        if p <= low_amber:
            return "AMBER"
        return "GREEN"

    raise ValueError("Unknown direction")


def realized_vol_annual(returns, window_days):
    return returns.rolling(window_days).std() * math.sqrt(252)


def max_drawdown(prices, window_days):
    roll_max = prices.rolling(window_days).max()
    return prices / roll_max - 1.0


def percentile_rank_last(x):
    if len(x) < 5:
        return np.nan
    last = x.iloc[-1]
    return (x <= last).mean()


def reer_5y_percentile(reer_monthly, window_months=60):
    reer = reer_monthly.dropna()
    reer_window = reer.iloc[-window_months:]
    return percentile_rank_last(reer_window)


def change_over_months(monthly_series, months=3):
    s = monthly_series.dropna()
    if len(s) < months + 1:
        return np.nan
    return s.iloc[-1] - s.iloc[-(months + 1)]
