import sqlite3
import pandas as pd
from config import DB_PATH

con = sqlite3.connect(DB_PATH)
print(pd.read_sql(
    "SELECT date, close FROM prices WHERE asset = 'BTC-USD' ORDER BY date LIMIT 3", con))