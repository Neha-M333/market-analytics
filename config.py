ASSETS = {
    "^NSEI":       ("Nifty 50",            "Equity Index", "INR"),
    "^GSPC":       ("S&P 500",             "Equity Index", "USD"),
    "GC=F":        ("Gold",                "Commodity",    "USD"),
    "CL=F":        ("Crude Oil",           "Commodity",    "USD"),
    "INR=X":       ("USD/INR",             "Currency",     "INR"),
    "BTC-USD":     ("Bitcoin",             "Crypto",       "USD"),
    "TLT":         ("US Treasury 20Y+ ETF","Bond",         "USD"),
    "TCS.NS":      ("TCS",                 "Equity",       "INR"),
    "HDFCBANK.NS": ("HDFC Bank",           "Equity",       "INR"),
    "RELIANCE.NS": ("Reliance",            "Equity",       "INR"),
}
STOCKS = ["TCS.NS", "HDFCBANK.NS", "RELIANCE.NS"]
DB_PATH = "market.db"
PERIOD = "5y"
BANKS = ["HDFCBANK.NS"]

# Company-reported figures that replace vendor statement data where we found a discrepancy.
# Values in INR (full units).
OVERRIDES = {
    "HDFCBANK.NS": {
        "net_income": 760_260_000_000,   # consolidated PAT FY26 - confirm attributable-to-owners figure
        "equity":     6_084_440_000_000, # consolidated net worth FY26
        "source": "company-reported FY26 consolidated results (hdfcbank.com); "
                  "yfinance statement equity 8,167bn disagreed with reported net worth",
    },
}

RISK_FREE_RATE = 0.0          # annual; state this assumption in the README
ANN_FACTOR = {"BTC-USD": 365} # everything else defaults to 252
DEFAULT_ANN_FACTOR = 252

# Large moves that were reviewed and matched to a real event (verify each before adding)
KNOWN_EVENTS = {
    ("HDFCBANK.NS", "2022-04-04"): "HDFC Ltd merger announcement",
    ("CL=F", "2021-11-26"): "Omicron variant sell-off",
    ("CL=F", "2022-03-09"): "Oil retreat after early-March 2022 spike",
    ("CL=F", "2026-04-08"): "Two-week US-Iran ceasefire announcement; WTI May closed at 94.41 (confirmed against news report)",
    ("CL=F", "2026-04-17"): "Oil fell as Middle East war-risk premium eased (Brent -10-11% that day)",
}