from __future__ import annotations

from urllib.parse import urlencode

import pandas as pd
import yfinance as yf


def fetch_yahoo_adjclose(tickers, start="2000-01-01"):
    df = yf.download(
        tickers=tickers,
        start=start,
        auto_adjust=True,
        progress=False,
    )["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return df.dropna(how="all")


def fetch_fred_series(series_id, start="1990-01-01"):
    """Fetch one FRED series without pandas_datareader.

    pandas_datareader currently imports distutils, which is unavailable in
    Python 3.12+ environments such as some Streamlit Cloud builds. This uses
    FRED's public CSV endpoint directly instead.
    """
    params = urlencode({"id": series_id, "observation_start": start})
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?{params}"

    df = pd.read_csv(url)
    if "observation_date" not in df.columns or series_id not in df.columns:
        raise ValueError(f"Unexpected FRED response for series {series_id}.")

    df["observation_date"] = pd.to_datetime(df["observation_date"])
    values = pd.to_numeric(df[series_id], errors="coerce")
    series = pd.Series(values.to_numpy(), index=df["observation_date"], name=series_id)
    return series.dropna()
