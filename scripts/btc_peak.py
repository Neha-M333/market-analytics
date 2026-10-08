import sqlite3
import pandas as pd
from config import DB_PATH

df = pd.read_sql("SELECT date, close FROM prices WHERE asset = 'BTC-USD' ORDER BY close DESC LIMIT 1",
                 sqlite3.connect(DB_PATH))
print(df)