import sqlite3
import numpy as np
import pandas as pd
from config import DB_PATH, RISK_FREE_RATE, ANN_FACTOR, DEFAULT_ANN_FACTOR


def get_prices(con):
    """Wide table: one row per date, one column per asset (NaN where it didn't trade)."""
    df = pd.read_sql("SELECT date, asset, close FROM prices", con, parse_dates=["date"])
    return df.pivot(index="date", columns="asset", values="close").sort_index()


def get_returns(prices):
    """Daily returns computed on each asset's OWN trading days (no forward-fill)."""
    cols = {c: prices[c].dropna().pct_change() for c in prices.columns}
    return pd.DataFrame(cols).sort_index()


def ann_factor(asset):
    return ANN_FACTOR.get(asset, DEFAULT_ANN_FACTOR)


def cagr(prices_series):
    s = prices_series.dropna()
    years = (s.index[-1] - s.index[0]).days / 365.25
    return (s.iloc[-1] / s.iloc[0]) ** (1 / years) - 1


def volatility(returns_series, factor):
    return returns_series.dropna().std(ddof=1) * np.sqrt(factor)


def max_drawdown(returns_series):
    r = returns_series.dropna()
    wealth = (1 + r).cumprod()
    drawdown = wealth / wealth.cummax() - 1
    return drawdown.min(), drawdown.idxmin()


def risk_return_table(prices, returns):
    rows = []
    for a in prices.columns:
        f = ann_factor(a)
        ret = cagr(prices[a])
        vol = volatility(returns[a], f)
        mdd, mdd_date = max_drawdown(returns[a])
        rows.append({
            "asset": a,
            "ann_return": ret,
            "ann_vol": vol,
            "sharpe": (ret - RISK_FREE_RATE) / vol,
            "max_drawdown": mdd,
            "max_dd_date": mdd_date.date(),
        })
    return pd.DataFrame(rows).set_index("asset")


def correlation_matrix(returns, min_periods=250):
    """Pairwise correlation of daily returns; needs at least min_periods overlapping days."""
    return returns.corr(min_periods=min_periods)


if __name__ == "__main__":
    con = sqlite3.connect(DB_PATH)
    prices = get_prices(con)
    returns = get_returns(prices)
    pd.set_option("display.width", 200)
    print(risk_return_table(prices, returns).round(3))
    print()
    print(correlation_matrix(returns).round(2))