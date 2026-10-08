import sqlite3
import pandas as pd
from run_queries import load_queries

con = sqlite3.connect("market.db")
queries = load_queries()

# Check 1: average daily return for Gold, computed in SQL
mean_sql = pd.read_sql(
    "SELECT AVG(ret) * 100 AS mean_pct FROM daily_returns "
    "WHERE asset = 'GC=F' AND ret IS NOT NULL",
    con,
)
print("SQL mean daily return (%):", mean_sql.iloc[0, 0])

# Check 2: latest 30-day annualized volatility for Gold, from your Q4
vol = pd.read_sql(queries["q4_rolling_vol_30d"].rstrip(";"), con)
gold_vol = vol[vol["asset"] == "GC=F"].tail(1)
print("SQL latest 30d volatility (%):")
print(gold_vol.to_string(index=False))