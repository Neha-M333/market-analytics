import sqlite3
import pandas as pd

con = sqlite3.connect("market.db")

print(pd.read_sql("""
    SELECT asset, COUNT(*) AS n, MIN(date) AS first, MAX(date) AS last
    FROM prices GROUP BY asset ORDER BY n
""", con))

print(pd.read_sql("SELECT * FROM fundamentals", con))