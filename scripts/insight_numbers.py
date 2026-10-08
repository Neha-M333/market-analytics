import sqlite3
import pandas as pd
from config import DB_PATH
from metrics import get_prices, get_returns, risk_return_table

con = sqlite3.connect(DB_PATH)
p = get_prices(con)
t = risk_return_table(p, get_returns(p))
t = t.loc[["BTC-USD", "^GSPC", "GC=F", "^NSEI"]]
t["ann_return"] *= 100
t["ann_vol"] *= 100
t["max_drawdown"] *= 100
print(t.round(2).to_string())
print()
print("BTC vol / S&P vol:", round(t.loc["BTC-USD", "ann_vol"] / t.loc["^GSPC", "ann_vol"], 2))
print("Window:", p.index.min().date(), "to", p.index.max().date())