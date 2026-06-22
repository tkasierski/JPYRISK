import pandas as pd

from jpy_risk.indices import exporter_pressure_index, macro_stress_index
from jpy_risk.utils import classify_percentile


def test_classify_percentile_higher_is_risk():
    assert classify_percentile(0.85, "higher_is_risk") == "RED"
    assert classify_percentile(0.75, "higher_is_risk") == "AMBER"
    assert classify_percentile(0.50, "higher_is_risk") == "GREEN"


def test_classify_percentile_lower_is_risk():
    assert classify_percentile(0.10, "lower_is_risk") == "RED"
    assert classify_percentile(0.25, "lower_is_risk") == "AMBER"
    assert classify_percentile(0.50, "lower_is_risk") == "GREEN"


def test_indices_return_values_when_components_present():
    df = pd.DataFrame(
        [
            {"indicator": "China vs Japan export growth spread (YoY, 3m avg)", "percentile": 0.8},
            {"indicator": "China vs Japan REER spread 3m change (monthly)", "percentile": 0.2},
            {"indicator": "Japan REER level (monthly)", "percentile": 0.7},
            {"indicator": "Japan 10Y yield 3m change (monthly)", "percentile": 0.6},
            {"indicator": "Nikkei 225 3m realized vol (ann.)", "percentile": 0.7},
            {"indicator": "USDJPY 3m realized vol (ann.)", "percentile": 0.5},
        ]
    )

    epi, epi_missing = exporter_pressure_index(df)
    msi, msi_missing = macro_stress_index(df)

    assert epi_missing == []
    assert msi_missing == []
    assert 0 <= epi <= 100
    assert 0 <= msi <= 100
