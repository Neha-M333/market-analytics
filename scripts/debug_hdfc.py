import yfinance as yf
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.float_format", "{:,.0f}".format)

tk = yf.Ticker("HDFCBANK.NS")

print("NET INCOME rows (all years):")
print(tk.financials.loc[["Net Income Common Stockholders", "Net Income"]])

print("\nBALANCE SHEET rows (all years):")
print(tk.balance_sheet.loc[["Stockholders Equity", "Common Stock Equity", "Total Assets", "Total Debt"]])

print("\nyfinance info ROE:", tk.info.get("returnOnEquity"))