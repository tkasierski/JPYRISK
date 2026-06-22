from __future__ import annotations

import numpy as np


def _index_from_components(df, components, name_for_errors="Index"):
    """
    Generic 0-100 index where higher is worse.

    components: dict of indicator_name -> (weight, direction)
    direction: higher_is_risk or lower_is_risk
    """
    total_w = 0.0
    score = 0.0
    missing = []

    for ind_name, (w, direction) in components.items():
        row = df[df["indicator"] == ind_name]
        if row.empty:
            missing.append(ind_name)
            continue

        p = row["percentile"].iloc[0]
        if p is None or (isinstance(p, float) and np.isnan(p)):
            missing.append(ind_name)
            continue

        if direction == "higher_is_risk":
            bad = float(p)
        elif direction == "lower_is_risk":
            bad = 1.0 - float(p)
        else:
            bad = float(p)

        score += w * bad
        total_w += w

    if total_w == 0:
        return np.nan, missing

    return 100.0 * (score / total_w), missing


def exporter_pressure_index(df):
    """Exporter Pressure Index, scaled 0-100. Higher is worse for Japan exporters."""
    components = {
        "China vs Japan export growth spread (YoY, 3m avg)": (0.40, "higher_is_risk"),
        "China vs Japan REER spread 3m change (monthly)": (0.35, "lower_is_risk"),
        "Japan REER level (monthly)": (0.25, "higher_is_risk"),
    }
    return _index_from_components(df, components, name_for_errors="EPI")


def macro_stress_index(df):
    """Macro Stress Index, scaled 0-100. Higher is worse for Japan equities."""
    components = {
        "Japan 10Y yield 3m change (monthly)": (0.45, "higher_is_risk"),
        "Nikkei 225 3m realized vol (ann.)": (0.35, "higher_is_risk"),
        "USDJPY 3m realized vol (ann.)": (0.20, "higher_is_risk"),
    }
    return _index_from_components(df, components, name_for_errors="MSI")


def label_0_100(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "Unavailable"
    if x >= 80:
        return "Severe"
    if x >= 65:
        return "Elevated"
    if x >= 50:
        return "Moderate"
    if x >= 35:
        return "Mild"
    return "Benign"
