import yfinance as yf

for t in ["RELIANCE.NS", "HDFCBANK.NS", "TCS.NS"]:
    tk = yf.Ticker(t)
    print("\n====", t, "====")
    print("INCOME STATEMENT rows:", tk.financials.index.tolist())
    print("BALANCE SHEET rows:", tk.balance_sheet.index.tolist())