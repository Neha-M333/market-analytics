import sqlite3
import pandas as pd
from config import DB_PATH


def load_queries(path="queries.sql"):
    sections = open(path).read().split("-- name:")[1:]
    queries = {}
    for s in sections:
        name, sql = s.split("\n", 1)
        queries[name.strip()] = sql.strip()
    return queries


def run(name, con, queries):
    return pd.read_sql(queries[name].rstrip(";"), con)


if __name__ == "__main__":
    con = sqlite3.connect(DB_PATH)
    queries = load_queries()
    con.executescript(queries["setup"])
    for name in queries:
        if name == "setup":
            continue
        print(f"\n=== {name} ===")
        print(run(name, con, queries).head(15).to_string(index=False))