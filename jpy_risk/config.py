CONFIG = {
    "asof_tz": "America/Denver",
    "lookbacks": {
        "realized_vol_days": 63,
        "drawdown_days": 252,
        "fx_move_days": 21,
        "reer_window_months": 60,
        "rate_change_months": 3,
    },
    "percentile_thresholds": {
        "amber": 0.70,
        "red": 0.80,
    },
    "history_windows": {
        "monthly_years": 10,
        "daily_years": 10,
    },
    "assets": {
        "nikkei": "^N225",
        "usdjpy": "JPY=X",
    },
    "fred_series": {
        "jgb10y": "IRLTLT01JPM156N",
        "reer_japan": "RBJPBIS",
        "reer_china": "RBCNBIS",
        "exports_japan": "XTEXVA01JPM667S",
        "exports_china": "XTEXVA01CNM667S",
        "cpi_core_yoy": None,
    },
}
