from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

from jpy_risk.config import CONFIG
from jpy_risk.data import fetch_fred_series, fetch_yahoo_adjclose
from jpy_risk.utils import classify_percentile, max_drawdown, percentile_of_last, realized_vol_annual, safe_float


def build_signals():
    asof = dt.datetime.now(dt.timezone.utc)

    px = fetch_yahoo_adjclose(
        [CONFIG["assets"]["nikkei"], CONFIG["assets"]["usdjpy"]],
        start="2000-01-01",
    )

    nikkei = px[CONFIG["assets"]["nikkei"]].dropna()
    usdjpy = px[CONFIG["assets"]["usdjpy"]].dropna()

    nikkei_ret = nikkei.pct_change().dropna()
    usdjpy_ret = usdjpy.pct_change().dropna()

    daily_hist_len = 252 * CONFIG["history_windows"]["daily_years"]
    monthly_hist_len = 12 * CONFIG["history_windows"]["monthly_years"]

    nikkei_vol_series = realized_vol_annual(
        nikkei_ret, CONFIG["lookbacks"]["realized_vol_days"]
    ).dropna()
    nikkei_vol_value = nikkei_vol_series.iloc[-1] if len(nikkei_vol_series) else np.nan
    nikkei_vol_pctl = percentile_of_last(nikkei_vol_series.tail(daily_hist_len))

    nikkei_dd_series = max_drawdown(
        nikkei, CONFIG["lookbacks"]["drawdown_days"]
    ).dropna()
    nikkei_dd_value = nikkei_dd_series.iloc[-1] if len(nikkei_dd_series) else np.nan
    nikkei_dd_pctl = percentile_of_last(nikkei_dd_series.tail(daily_hist_len))

    usdjpy_vol_series = realized_vol_annual(
        usdjpy_ret, CONFIG["lookbacks"]["realized_vol_days"]
    ).dropna()
    usdjpy_vol_value = usdjpy_vol_series.iloc[-1] if len(usdjpy_vol_series) else np.nan
    usdjpy_vol_pctl = percentile_of_last(usdjpy_vol_series.tail(daily_hist_len))

    fx_move_days = CONFIG["lookbacks"]["fx_move_days"]
    usdjpy_1m_move_series = usdjpy.pct_change(fx_move_days).dropna()
    usdjpy_1m_move_value = usdjpy_1m_move_series.iloc[-1] if len(usdjpy_1m_move_series) else np.nan
    usdjpy_1m_move_abs_pctl = percentile_of_last(usdjpy_1m_move_series.abs().tail(daily_hist_len))

    jgb10y = fetch_fred_series(CONFIG["fred_series"]["jgb10y"], start="1990-01-01")
    reer_jp = fetch_fred_series(CONFIG["fred_series"]["reer_japan"], start="1994-01-01")

    reer_jp_level_series = reer_jp.dropna()
    reer_jp_level_value = reer_jp_level_series.iloc[-1] if len(reer_jp_level_series) else np.nan
    reer_jp_level_pctl = percentile_of_last(reer_jp_level_series.tail(monthly_hist_len))

    rate_change_months = CONFIG["lookbacks"]["rate_change_months"]
    jgb10y_3mchg_series = jgb10y.dropna().diff(rate_change_months).dropna()
    jgb10y_3mchg_value = jgb10y_3mchg_series.iloc[-1] if len(jgb10y_3mchg_series) else np.nan
    jgb10y_3mchg_pctl = percentile_of_last(jgb10y_3mchg_series.tail(monthly_hist_len))

    exports_jp = fetch_fred_series(CONFIG["fred_series"]["exports_japan"], start="1992-01-01")
    exports_cn = fetch_fred_series(CONFIG["fred_series"]["exports_china"], start="1992-01-01")
    exports = pd.concat([exports_cn, exports_jp], axis=1).dropna()
    exports.columns = ["exports_cn", "exports_jp"]

    cn_yoy = exports["exports_cn"].pct_change(12)
    jp_yoy = exports["exports_jp"].pct_change(12)
    spread_yoy = (cn_yoy - jp_yoy).rolling(3).mean().dropna()
    export_spread_value = spread_yoy.iloc[-1] if len(spread_yoy) else np.nan
    export_spread_pctl = percentile_of_last(spread_yoy.tail(monthly_hist_len))

    reer_cn = fetch_fred_series(CONFIG["fred_series"]["reer_china"], start="1994-01-01")
    reer_pair = pd.concat([reer_cn, reer_jp], axis=1).dropna()
    reer_pair.columns = ["reer_cn", "reer_jp"]
    reer_spread = (reer_pair["reer_cn"] - reer_pair["reer_jp"]).dropna()
    reer_spread_3mchg = reer_spread.diff(CONFIG["lookbacks"]["rate_change_months"]).dropna()
    reer_spread_3mchg_value = reer_spread_3mchg.iloc[-1] if len(reer_spread_3mchg) else np.nan
    reer_spread_3mchg_pctl = percentile_of_last(reer_spread_3mchg.tail(monthly_hist_len))

    rows = []

    def add_row(name, value, unit, pctl, direction, detail, source):
        rows.append(
            {
                "indicator": name,
                "value": safe_float(value),
                "unit": unit,
                "percentile": safe_float(pctl),
                "state": classify_percentile(pctl, direction=direction),
                "detail": detail,
                "source": source,
            }
        )

    add_row(
        "Nikkei 225 3m realized vol (ann.)",
        nikkei_vol_value,
        "vol",
        nikkei_vol_pctl,
        "higher_is_risk",
        "Realized vol from daily returns, 63d window, annualized(252). Percentile vs last 10y daily history of this indicator.",
        "Yahoo Finance (^N225)",
    )
    add_row(
        "Nikkei 225 drawdown vs 1y rolling peak",
        nikkei_dd_value,
        "drawdown",
        nikkei_dd_pctl,
        "lower_is_risk",
        "Current drawdown vs trailing 252d rolling max. Percentile vs last 10y daily history (more negative = worse).",
        "Yahoo Finance (^N225)",
    )
    add_row(
        "USDJPY 3m realized vol (ann.)",
        usdjpy_vol_value,
        "vol",
        usdjpy_vol_pctl,
        "higher_is_risk",
        "Realized vol from daily returns, 63d window, annualized(252). Percentile vs last 10y daily history of this indicator.",
        "Yahoo Finance (JPY=X)",
    )
    add_row(
        "USDJPY 1m move (abs)",
        usdjpy_1m_move_value,
        "% move",
        usdjpy_1m_move_abs_pctl,
        "higher_is_risk",
        "Absolute percent change over last 21 trading days. Percentile computed on absolute history over last 10y daily.",
        "Yahoo Finance (JPY=X)",
    )
    add_row(
        "Japan 10Y yield 3m change (monthly)",
        jgb10y_3mchg_value,
        "pp",
        jgb10y_3mchg_pctl,
        "higher_is_risk",
        "Monthly series: latest minus 3 months prior. Percentile vs last 10y monthly history of this 3m-change indicator.",
        "FRED IRLTLT01JPM156N",
    )
    add_row(
        "China vs Japan export growth spread (YoY, 3m avg)",
        export_spread_value,
        "spread",
        export_spread_pctl,
        "higher_is_risk",
        "China exports YoY minus Japan exports YoY, smoothed with 3m moving average.",
        "FRED XTEXVA01CNM667S, XTEXVA01JPM667S",
    )
    add_row(
        "China vs Japan REER spread 3m change (monthly)",
        reer_spread_3mchg_value,
        "index_pts",
        reer_spread_3mchg_pctl,
        "lower_is_risk",
        "3m change in China REER minus Japan REER. Negative values indicate China becoming relatively cheaper vs Japan.",
        "FRED RBCNBIS, RBJPBIS",
    )
    add_row(
        "Japan REER level (monthly)",
        reer_jp_level_value,
        "index",
        reer_jp_level_pctl,
        "higher_is_risk",
        "Japan REER level vs last 10y monthly history.",
        "FRED RBJPBIS",
    )

    df = pd.DataFrame(rows)
    df["asof_utc"] = asof.isoformat()
    df["percentile_amber"] = CONFIG["percentile_thresholds"]["amber"]
    df["percentile_red"] = CONFIG["percentile_thresholds"]["red"]
    df["history_window_daily_years"] = CONFIG["history_windows"]["daily_years"]
    df["history_window_monthly_years"] = CONFIG["history_windows"]["monthly_years"]
    return df
