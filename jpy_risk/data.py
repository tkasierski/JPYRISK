from __future__ import annotations

import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr


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
    s = pdr.DataReader(series_id, "fred", start=start)[series_id]
    return s.dropna()
