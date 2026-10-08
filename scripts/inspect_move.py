import sqlite3, sys
import pandas as pd

asset, date = sys.argv[1], sys.argv[2]
con = sqlite3.connect("market.db")
df = pd.read_sql("SELECT date, close FROM prices WHERE asset=? ORDER BY date", con, params=[asset])
df["ret_%"] = (df["close"].pct_change() * 100).round(2)
i = df.index[df["date"] == date][0]
print(df.iloc[max(i - 3, 0): i + 4].to_string(index=False))