import sqlite3
import pandas as pd
from config import DB_PATH

print(pd.read_sql(
    "SELECT asset, pe, roe, debt_to_equity, equity_multiplier, as_of FROM fundamentals",
    sqlite3.connect(DB_PATH)).round(3).to_string(index=False))