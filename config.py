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