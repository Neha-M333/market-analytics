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

# Company-reported figures replacing vendor statement data where we found a discrepancy.
# Values in INR (1 crore = 10,000,000). Source: HDFC Bank audited consolidated results,
# quarter and year ended March 31, 2026 (Board approved April 18, 2026).
OVERRIDES = {
    "HDFCBANK.NS": {
        "net_income": 760_259_700_000,      # 76,025.97 cr: consolidated profit after minority interest
        "equity":     5_860_594_700_000,    # 586,059.47 cr: capital + ESOP outstanding + reserves and surplus
        "assets":     49_080_408_400_000,   # 4,908,040.84 cr: consolidated total assets
        "source": "HDFC Bank audited consolidated results FY2025-26 (18 Apr 2026); vendor statement "
                  "equity and assets disagreed with the filing",
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