import sqlite3, pandas as pd
con = sqlite3.connect("market.db")
g = pd.read_sql("SELECT date, close FROM prices WHERE asset='GC=F' ORDER BY date", con)
g["ret"] = g["close"].pct_change()
print(g["ret"].mean() * 100)                         # compare to Gold's average return
print(g["ret"].rolling(30).std().iloc[-1] * 252**0.5 * 100)   # compare to the last vol_30d row