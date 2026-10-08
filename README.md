# Multi-Asset Market Analytics

A dashboard that puts equities, commodities, currency, crypto and bonds on one risk-adjusted scale, with an automated data-quality layer. Built with Python, SQLite, pandas, yfinance and Streamlit.

![Risk & Return tab](docs/risk_return.png)

## Customer and problem
**Customer:** a retail investor or junior portfolio analyst comparing assets across markets.
**Problem:** returns, risk and data reliability usually sit in separate tools, in different currencies and calendars, so it is hard to see which asset actually paid for its risk, and whether the data can be trusted.

## What it does
- **Asset Class Overview:** rebased price history and average daily return by class (SQL)
- **Risk & Return:** annualized return, volatility, Sharpe, max drawdown, drawdown chart
- **Correlation:** daily or weekly return correlation heatmap
- **Stock Fundamentals:** P/E, ROE, leverage for TCS, HDFC Bank, Reliance; banks ranked on equity multiplier, not debt/equity
- **Data Health:** automated checks for stale data, gaps, flat prices and large moves

## Insights (5 years to 8 Oct 2026)
1. **Gold vs Nifty 50.** Gold returned 18.8% a year with a Sharpe of 0.99; the Nifty returned 4.7% with 0.34. But gold's maximum drawdown (-24.9%, July 2026) was deeper than the Nifty's (-17.2%). Gold is not a drawdown hedge here, though its return per unit of risk was far higher. Gold is a USD futures series and the Nifty is in INR, and the window includes a strong gold run.
2. **Bitcoin vs S&P 500.** Bitcoin returned 8.8% a year against 12.2% for the S&P 500, with about 3x the volatility (51% vs 17%) and a -76.6% drawdown versus -25.4%. Sharpe was 0.17 vs 0.72. The window starts at [first close, $53,968, and where the peak falls], so the result is sensitive to the start date.
3. **Cross-market correlation.** Nifty and S&P 500 daily return correlation is 0.19, rising to 0.43 on weekly returns, consistent with the two markets closing at different times. Bitcoin's correlation with the S&P moved the other way (0.42 daily, 0.28 weekly), which I did not investigate.

## Data quality and validation
- SQL window-function results were validated against pandas: means match exactly; 30-day volatility differs by the expected factor of sqrt(29/30) (population vs sample standard deviation).
- Three unit tests cover max drawdown, volatility and CAGR on hand-calculated cases. The drawdown function also reproduces known troughs (S&P 500 Oct 2022, Bitcoin Nov 2022).
- **HDFC Bank reconciliation.** Vendor statement equity (₹8.17tn) and total assets (₹52.6tn) disagreed with the bank's audited FY26 consolidated results (shareholders' equity ₹5.86tn, total assets ₹49.1tn), so I used the audited figures (override documented in `config.py`). A first attempt that used total equity including minority interest understated ROE; the corrected ROE of 13.0% (13.7% on average equity) is consistent with the vendor's 13.8%.
- `checks.py` flagged 10 large daily moves. [N] are matched to events; the rest are marked `review`. The WTI -16.4% drop on 8 Apr 2026 was confirmed against a news report (May contract closed at 94.41, matching the stored price).

## Assumptions and limitations
- Risk-free rate 0% in Sharpe; volatility annualized with 252 days (365 for Bitcoin); return is CAGR.
- Returns are in each asset's local currency. USD/INR is an exchange rate, so its "return" is rupee depreciation.
- Gold and oil are futures series and can jump when contracts roll.
- Fundamentals are a single snapshot (FY ended 31 Mar 2026), not history. ROE uses year-end equity.
- Same-day cross-region correlations are understated because markets close at different times.

## Run it
```
pip install -r requirements.txt
python etl.py
python checks.py
streamlit run app.py
python -m pytest
```

## Next feature
A portfolio builder: the user sets weights across the assets and sees portfolio return, volatility, drawdown and the diversification effect from the correlation matrix. Single-asset metrics are the first thing an investor sees, but the real question is how assets behave together.