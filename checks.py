import sqlite3
import pandas as pd
from metrics import get_prices, get_returns
from config import DB_PATH, KNOWN_EVENTS

DEFAULT_JUMP = 0.10                 # flag daily moves above 10%
JUMP_OVERRIDE = {"BTC-USD": 0.20}   # crypto is naturally more volatile
STALE_DAYS = 5                      # latest price older than this is suspicious
GAP_DAYS = 6                        # calendar days between consecutive prices
FLAT_RUN = 5                        # identical closes in a row


def issue(check, asset, when, detail, severity):
    return {"check": check, "asset": asset, "date": str(when),
            "detail": detail, "severity": severity}


def check_staleness(prices):
    out, today = [], pd.Timestamp.today().normalize()
    for a in prices.columns:
        last = prices[a].dropna().index[-1]
        age = (today - last).days
        if age > STALE_DAYS:
            out.append(issue("stale_data", a, last.date(),
                             f"last price is {age} days old", "high"))
    return out


def check_jumps(returns):
    out = []
    for a in returns.columns:
        limit = JUMP_OVERRIDE.get(a, DEFAULT_JUMP)
        r = returns[a].dropna()
        for d, v in r[r.abs() > limit].items():
            detail = f"{v:+.1%} in one day (limit {limit:.0%})"
            note = KNOWN_EVENTS.get((a, str(d.date())))
            if note:
                out.append(issue("large_move", a, d.date(), f"{detail} - {note}", "explained"))
            else:
                out.append(issue("large_move", a, d.date(), detail, "review"))
    return out


def check_gaps(prices):
    out = []
    for a in prices.columns:
        idx = prices[a].dropna().index
        gaps = pd.Series(idx[1:] - idx[:-1], index=idx[1:])
        for d, g in gaps[gaps.dt.days > GAP_DAYS].items():
            out.append(issue("date_gap", a, d.date(),
                             f"{g.days} days since previous price", "medium"))
    return out


def check_flat_runs(prices):
    out = []
    for a in prices.columns:
        s = prices[a].dropna()
        same = s.diff() == 0
        run = same.groupby((~same).cumsum()).cumsum()   # length of current run of repeats
        for d in run[run == FLAT_RUN].index:
            out.append(issue("flat_price", a, d.date(),
                             f"price unchanged for {FLAT_RUN}+ days", "medium"))
    return out


def run_all():
    con = sqlite3.connect(DB_PATH)
    prices = get_prices(con)
    returns = get_returns(prices)
    issues = (check_staleness(prices) + check_jumps(returns)
              + check_gaps(prices) + check_flat_runs(prices))
    df = pd.DataFrame(issues, columns=["check", "asset", "date", "detail", "severity"])
    df["checked_at"] = pd.Timestamp.now().isoformat(timespec="seconds")
    df.to_sql("data_quality", con, if_exists="replace", index=False)
    con.close()
    return df


if __name__ == "__main__":
    df = run_all()
    if df.empty:
        print("No issues found")
    else:
        print(df.groupby(["check", "severity"]).size(), "\n")
        print(df.sort_values(["asset", "date"]).to_string(index=False))