import sqlite3
from config import DB_PATH
from metrics import get_prices, get_returns, correlation_matrix

con = sqlite3.connect(DB_PATH)
p = get_prices(con)
daily = correlation_matrix(get_returns(p), min_periods=250)
weekly = correlation_matrix(get_returns(p.resample("W-FRI").last()), min_periods=100)

for a, b in [("^NSEI", "^GSPC"), ("BTC-USD", "^GSPC"), ("GC=F", "^GSPC"), ("TLT", "^GSPC")]:
    print(f"{a} vs {b}: daily {daily.loc[a, b]:.2f} | weekly {weekly.loc[a, b]:.2f}")