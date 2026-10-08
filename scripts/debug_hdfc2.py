import yfinance as yf
import pandas as pd

pd.set_option("display.width", 220)
pd.set_option("display.float_format", "{:,.0f}".format)

tk = yf.Ticker("HDFCBANK.NS")
bs = tk.balance_sheet

rows = [
    "Stockholders Equity", "Total Equity Gross Minority Interest", "Minority Interest",
    "Capital Stock", "Additional Paid In Capital", "Retained Earnings",
    "Other Equity Interest", "Gains Losses Not Affecting Retained Earnings",
    "Other Equity Adjustments", "Treasury Stock",
]
print(bs.reindex(rows))

info = tk.info
bv, sh = info.get("bookValue"), info.get("sharesOutstanding")
print("\nbookValue per share:", bv, "| shares outstanding:", sh)
if bv and sh:
    print("Implied equity (bookValue x shares): {:,.0f}".format(bv * sh))
print("priceToBook:", info.get("priceToBook"), "| ROE:", info.get("returnOnEquity"))