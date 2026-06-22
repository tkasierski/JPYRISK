from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import streamlit as st

from jpy_risk.indices import exporter_pressure_index, label_0_100, macro_stress_index
from jpy_risk.narrative import generate_narrative
from jpy_risk.pdf import export_pdf
from jpy_risk.signals import build_signals


st.set_page_config(page_title="JPY Risk Monitor", layout="wide")

st.title("Japan Equity Risk Monitor")
st.write(
    "Monitor Japan equity, FX, rates, and exporter-pressure risk using Yahoo Finance and FRED data."
)


def _state_badge(state: str) -> str:
    if state == "RED":
        return "🔴 RED"
    if state == "AMBER":
        return "🟠 AMBER"
    if state == "GREEN":
        return "🟢 GREEN"
    return "⚪ GRAY"


run_button = st.button("Run monitor", type="primary")

if run_button:
    with st.spinner("Fetching market and macro data..."):
        try:
            df = build_signals()
            narrative = generate_narrative(df)
            epi, epi_missing = exporter_pressure_index(df)
            msi, msi_missing = macro_stress_index(df)
        except Exception as exc:
            st.error(f"Error: {exc}")
            st.stop()

    st.success("Monitor updated.")
    st.caption(f"As of UTC: {df['asof_utc'].iloc[0]}")

    col1, col2 = st.columns(2)
    with col1:
        if isinstance(epi, float) and not np.isnan(epi):
            st.metric("Exporter Pressure Index", f"{epi:.1f}", label_0_100(epi))
        else:
            st.metric("Exporter Pressure Index", "Unavailable")
        if epi_missing:
            st.warning("Missing EPI components: " + "; ".join(epi_missing))

    with col2:
        if isinstance(msi, float) and not np.isnan(msi):
            st.metric("Macro Stress Index", f"{msi:.1f}", label_0_100(msi))
        else:
            st.metric("Macro Stress Index", "Unavailable")
        if msi_missing:
            st.warning("Missing MSI components: " + "; ".join(msi_missing))

    st.subheader("Executive summary")
    st.text(narrative)

    st.subheader("Indicator snapshot")
    display_df = df.copy()
    display_df["state"] = display_df["state"].map(_state_badge)
    display_df["percentile"] = display_df["percentile"].map(
        lambda x: np.nan if x is None or pd.isna(x) else x * 100
    )
    st.dataframe(
        display_df[
            [
                "state",
                "indicator",
                "value",
                "unit",
                "percentile",
                "source",
                "detail",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download indicator CSV",
        data=csv_bytes,
        file_name="jpy_risk_indicators.csv",
        mime="text/csv",
    )

    with TemporaryDirectory() as temp_dir:
        pdf_path = Path(temp_dir) / "japan_equity_risk_monitor.pdf"
        export_pdf(df, narrative, pdf_path)
        pdf_bytes = pdf_path.read_bytes()

    st.download_button(
        "Download PDF report",
        data=pdf_bytes,
        file_name="japan_equity_risk_monitor.pdf",
        mime="application/pdf",
    )
else:
    st.info("Click Run monitor to fetch the latest data and generate the report.")
    st.markdown(
        "**Streamlit deployment settings:** Repository `tkasierski/JPYRISK`, branch `main`, main file path `streamlit_app.py`."
    )
