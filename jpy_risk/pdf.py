from __future__ import annotations

import textwrap

import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from jpy_risk.indices import exporter_pressure_index, macro_stress_index


def _format_value(value, unit):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "NA"
    if unit == "drawdown":
        return f"{value * 100:.1f}%"
    if unit in ["% move", "spread"]:
        return f"{value * 100:.2f}%"
    if unit == "vol":
        return f"{value:.2f}"
    if unit == "pp":
        return f"{value:.2f}"
    return f"{value:.3f}"


def export_pdf(df, narrative, path, title="Japan Equity Risk Monitor"):
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"As of (UTC): {df['asof_utc'].iloc[0]}")
    y -= 16

    epi, _ = exporter_pressure_index(df)
    msi, _ = macro_stress_index(df)

    if isinstance(epi, float) and not np.isnan(epi):
        c.drawString(50, y, f"Exporter Pressure Index (0-100): {epi:.1f}")
        y -= 14
    if isinstance(msi, float) and not np.isnan(msi):
        c.drawString(50, y, f"Macro Stress Index (0-100): {msi:.1f}")
        y -= 14

    y -= 10

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Executive Summary")
    y -= 15

    c.setFont("Helvetica", 9)
    for line in narrative.split("\n"):
        wrapped = textwrap.wrap(line, width=95) or [""]
        for wrapped_line in wrapped:
            if y < 60:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 9)
            c.drawString(55, y, wrapped_line)
            y -= 11
        y -= 2

    y -= 10

    if y < 120:
        c.showPage()
        y = height - 50

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Indicator Snapshot (10y Percentile Framework)")
    y -= 18

    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "State")
    c.drawString(100, y, "Indicator")
    c.drawRightString(470, y, "Value")
    c.drawRightString(540, y, "Pctile")
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 12

    c.setFont("Helvetica", 9)
    for _, row in df.iterrows():
        if y < 60:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 9)

        percentile = row.get("percentile", np.nan)
        percentile = percentile * 100 if percentile is not None else np.nan
        pctl_str = "NA" if percentile is None or (isinstance(percentile, float) and np.isnan(percentile)) else f"{percentile:.1f}"

        c.drawString(50, y, str(row.get("state", "")))
        c.drawString(100, y, str(row.get("indicator", ""))[:50])
        c.drawRightString(470, y, _format_value(row.get("value", np.nan), row.get("unit", "")))
        c.drawRightString(540, y, pctl_str)
        y -= 12

    c.save()
    return str(path)
