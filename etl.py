import sqlite3
import pandas as pd
import yfinance as yf
from config import ASSETS, STOCKS, BANKS, OVERRIDES, DB_PATH, PERIOD


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


def latest_value(df, labels):
    """Return (period_end_date, value) for the first label that exists and has data."""
    for label in labels:
        if label in df.index:
            s = df.loc[label].dropna().sort_index()
            if len(s):
                return s.index[-1], float(s.iloc[-1])
    return None, None


def load_fundamentals(con):
    rows = []
    for t in STOCKS:
        tk = yf.Ticker(t)
        info = tk.info

        ni_date, net_income = latest_value(
            tk.financials, ["Net Income Common Stockholders", "Net Income"])
        eq_date, equity = latest_value(
            tk.balance_sheet, ["Stockholders Equity", "Common Stock Equity"])
        _, debt = latest_value(tk.balance_sheet, ["Total Debt"])
        _, assets = latest_value(tk.balance_sheet, ["Total Assets"])

        # Sanity: the income statement and balance sheet should be the same fiscal year
        if ni_date != eq_date:
            print(f"WARNING {t}: income date {ni_date} != balance date {eq_date}")

        source = "statements (roe, leverage); info (pe, market_cap)"
        if t in OVERRIDES:
            ov = OVERRIDES[t]
            net_income = ov["net_income"]
            equity = ov["equity"]
            assets = ov.get("assets", assets)
            source = ov["source"]

        rows.append({
            "asset": t,
            "pe": info.get("trailingPE"),
            "market_cap": info.get("marketCap"),
            "roe": net_income / equity if net_income and equity else None,
            "debt_to_equity": None if t in BANKS else (debt / equity if debt is not None and equity else None),
            "equity_multiplier": assets / equity if assets and equity else None,
            "is_bank": int(t in BANKS),
            "fiscal_year_end": str(eq_date.date()) if eq_date is not None else None,
            "source": source,
            "as_of": pd.Timestamp.today().date().isoformat(),
        })
    pd.DataFrame(rows).to_sql("fundamentals", con, if_exists="replace", index=False)

if __name__ == "__main__":
    con = sqlite3.connect(DB_PATH)
    load_assets(con)
    load_prices(con)
    load_fundamentals(con)
    con.close()
    print("Done")