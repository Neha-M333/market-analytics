import sqlite3
import pandas as pd
import yfinance as yf
from config import ASSETS, STOCKS, DB_PATH, PERIOD


def load_assets(con):
    df = pd.DataFrame(
        [(t, *v) for t, v in ASSETS.items()],
        columns=["ticker", "name", "asset_class", "currency"],
    )
    df.to_sql("assets", con, if_exists="replace", index=False)


def load_prices(con):
    # Extract: one download call for all tickers
    raw = yf.download(list(ASSETS), period=PERIOD, auto_adjust=True)["Close"]
    # Transform: wide table (one column per ticker) -> long table (date, asset, close)
    long = (
        raw.reset_index()
        .melt(id_vars="Date", var_name="asset", value_name="close")
        .dropna()
        .rename(columns={"Date": "date"})
    )
    long["date"] = long["date"].dt.strftime("%Y-%m-%d")
    # Load
    long.to_sql("prices", con, if_exists="replace", index=False)


def load_fundamentals(con):
    rows = []
    for t in STOCKS:
        info = yf.Ticker(t).info
        rows.append((
            t,
            info.get("trailingPE"),
            info.get("returnOnEquity"),
            info.get("debtToEquity"),
            info.get("marketCap"),
            pd.Timestamp.today().date().isoformat(),
        ))
    pd.DataFrame(
        rows,
        columns=["asset", "pe", "roe", "debt_to_equity", "market_cap", "as_of"],
    ).to_sql("fundamentals", con, if_exists="replace", index=False)


if __name__ == "__main__":
    con = sqlite3.connect(DB_PATH)
    load_assets(con)
    load_prices(con)
    load_fundamentals(con)
    con.close()
    print("Done")