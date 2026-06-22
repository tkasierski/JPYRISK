from __future__ import annotations

import numpy as np

from jpy_risk.indices import exporter_pressure_index, label_0_100, macro_stress_index


def _format_value(val, unit):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "NA"
    if unit == "drawdown":
        return f"{val * 100:.1f}%"
    if unit == "vol":
        return f"{val:.2f}"
    if unit in ["% move", "spread"]:
        return f"{val * 100:.1f}%"
    if unit == "pp":
        return f"{val:.2f} pp"
    return f"{val:.3f}"


def generate_narrative(df):
    epi, epi_missing = exporter_pressure_index(df)
    msi, msi_missing = macro_stress_index(df)

    lines = []
    if isinstance(epi, float) and not np.isnan(epi):
        lines.append(f"Exporter Pressure Index (0-100): {epi:.1f} - {label_0_100(epi)}.")
    else:
        lines.append("Exporter Pressure Index (0-100): Unavailable.")
    if epi_missing:
        lines.append("EPI missing components: " + "; ".join(epi_missing) + ".")

    if isinstance(msi, float) and not np.isnan(msi):
        lines.append(f"Macro Stress Index (0-100): {msi:.1f} - {label_0_100(msi)}.")
    else:
        lines.append("Macro Stress Index (0-100): Unavailable.")
    if msi_missing:
        lines.append("MSI missing components: " + "; ".join(msi_missing) + ".")

    lines.append("")

    buckets = {
        "China competitive pressure": [],
        "FX competitiveness and translation": [],
        "Rates and financial conditions": [],
        "Equity risk regime": [],
        "Other": [],
    }

    tripped = df[df["state"].isin(["AMBER", "RED"])].copy()
    if tripped.empty:
        lines.append("No indicators breached AMBER/RED percentile bands on this run.")
        return "\n".join(lines).strip()

    for _, row in tripped.iterrows():
        name = row["indicator"]
        state = row["state"]
        percentile = row["percentile"] * 100 if row["percentile"] is not None else np.nan
        value = _format_value(row["value"], row["unit"])

        if "China vs Japan export growth spread" in name:
            interp = "China export momentum is outpacing Japan, consistent with potential market-share and pricing pressure."
            bucket = "China competitive pressure"
        elif "China vs Japan REER spread" in name:
            interp = "Relative price competitiveness is shifting toward China, raising price-undercutting risk in global end-markets."
            bucket = "China competitive pressure"
        elif "Japan REER level" in name:
            interp = "Real JPY strength can be a pricing headwind for exporters and a margin risk if pass-through is limited."
            bucket = "FX competitiveness and translation"
        elif "USDJPY 3m realized vol" in name:
            interp = "FX volatility is elevated, increasing translation uncertainty and earnings revision risk."
            bucket = "FX competitiveness and translation"
        elif "USDJPY 1m move" in name:
            interp = "Large recent FX moves can affect guidance, hedges, and price/volume assumptions."
            bucket = "FX competitiveness and translation"
        elif "10Y yield" in name:
            interp = "Rates are moving quickly, which can tighten financial conditions and pressure equity multiples."
            bucket = "Rates and financial conditions"
        elif "Nikkei" in name and "realized vol" in name:
            interp = "Equity volatility is elevated, consistent with weaker risk appetite."
            bucket = "Equity risk regime"
        elif "drawdown" in name:
            interp = "Drawdown dynamics imply investor de-risking, which can pressure exporter-sensitive sectors."
            bucket = "Equity risk regime"
        else:
            interp = "Indicator is at an extreme versus its 10-year history."
            bucket = "Other"

        pctl_str = "NA" if percentile is None or np.isnan(percentile) else f"{percentile:.1f}"
        buckets[bucket].append(f"{state}: {name} | value {value} | pctile {pctl_str} | {interp}")

    for section, items in buckets.items():
        if not items:
            continue
        lines.append(section + ":")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).strip()
