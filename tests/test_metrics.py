import pandas as pd
import pytest
from metrics import max_drawdown, volatility, cagr


def test_max_drawdown_known_case():
    # prices 100 -> 120 -> 60 -> 90 : worst fall is from 120 to 60 = -50%
    prices = pd.Series([100, 120, 60, 90], dtype=float)
    mdd, _ = max_drawdown(prices.pct_change())
    assert mdd == pytest.approx(-0.5)


def test_volatility_of_constant_returns_is_zero():
    r = pd.Series([0.01] * 50)
    assert volatility(r, 252) == pytest.approx(0.0, abs=1e-12)


def test_cagr_doubling_in_one_year():
    idx = pd.to_datetime(["2020-01-01", "2020-12-31"])
    s = pd.Series([100.0, 200.0], index=idx)
    assert cagr(s) == pytest.approx(1.0, rel=0.01)