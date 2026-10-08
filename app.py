import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

from config import DB_PATH, RISK_FREE_RATE
from metrics import get_prices, get_returns, risk_return_table, correlation_matrix
from run_queries import load_queries, run

st.set_page_config(page_title="Multi-Asset Market Analytics", layout="wide")


@st.cache_data
def load_data():
    con = sqlite3.connect(DB_PATH)
    queries = load_queries()
    con.executescript(queries["setup"])
    data = {
        "prices": get_prices(con),
        "assets": pd.read_sql("SELECT * FROM assets", con),
        "fundamentals": pd.read_sql(
            "SELECT a.name, f.* FROM fundamentals f JOIN assets a ON a.ticker = f.asset", con),
        "q1": run("q1_avg_return_by_class", con, queries),
        "q5": run("q5_roe_vs_leverage", con, queries),
        "dq": pd.read_sql("SELECT * FROM data_quality", con),
    }
    con.close()
    return data


d = load_data()
prices, assets = d["prices"], d["assets"]
name_of = dict(zip(assets["ticker"], assets["name"]))
class_of = dict(zip(assets["ticker"], assets["asset_class"]))
returns_daily = get_returns(prices)

st.title("Multi-Asset Market Analytics")
st.caption(f"Data through {prices.index.max().date()} · prices adjusted for splits and dividends · "
           "returns in each asset's local currency")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Asset Class Overview", "Risk & Return", "Correlation", "Stock Fundamentals", "Data Health"])

# ---------- Tab 1 ----------
with tab1:
    classes = sorted(assets["asset_class"].unique())
    chosen = st.multiselect("Asset classes", classes, default=classes)
    years = st.slider("Look-back (years)", 1, 5, 5)
    start = prices.index.max() - pd.DateOffset(years=years)

    series = {}
    for t in prices.columns:
        if class_of[t] not in chosen:
            continue
        s = prices[t].dropna()
        s = s[s.index >= start]
        if len(s):
            series[name_of[t]] = s / s.iloc[0] * 100
    if series:
        fig = px.line(pd.DataFrame(series), labels={"value": "Rebased to 100", "variable": ""})
        fig.update_traces(connectgaps=True)
        st.plotly_chart(fig)

    st.subheader("Average daily return by asset class (from SQL)")
    st.dataframe(d["q1"], hide_index=True)
    st.caption("Crypto trades 365 days a year and the others about 252, so per-day averages are not "
               "directly comparable. Use the annualized figures in the next tab.")

# ---------- Tab 2 ----------
with tab2:
    rr = risk_return_table(prices, returns_daily).reset_index()
    rr["Asset"] = rr["asset"].map(name_of)
    rr["Class"] = rr["asset"].map(class_of)
    rr["Return (%)"] = rr["ann_return"] * 100
    rr["Volatility (%)"] = rr["ann_vol"] * 100
    rr["Max drawdown (%)"] = rr["max_drawdown"] * 100
    rr["Sharpe"] = rr["sharpe"]

    fig = px.scatter(rr, x="Volatility (%)", y="Return (%)", color="Class", text="Asset",
                     hover_data=["Sharpe", "Max drawdown (%)"])
    fig.update_traces(textposition="top center", marker_size=11)
    st.plotly_chart(fig)

    st.dataframe(
        rr[["Asset", "Class", "Return (%)", "Volatility (%)", "Sharpe", "Max drawdown (%)", "max_dd_date"]]
        .round(2).sort_values("Sharpe", ascending=False),
        hide_index=True)

    sel = st.selectbox("Drawdown history", list(prices.columns), format_func=lambda t: name_of[t])
    r = returns_daily[sel].dropna()
    wealth = (1 + r).cumprod()
    dd = (wealth / wealth.cummax() - 1) * 100
    st.plotly_chart(px.area(x=dd.index, y=dd.values, labels={"x": "Date", "y": "Drawdown (%)"}))

    st.caption(f"Assumptions: risk-free rate {RISK_FREE_RATE:.1%}; volatility annualized with 252 days "
               "(365 for BTC); return is CAGR. USD/INR is an exchange rate, so its 'return' is rupee "
               "depreciation. Gold and oil are futures, which can jump when contracts roll.")

# ---------- Tab 3 ----------
with tab3:
    freq = st.radio("Return frequency", ["Daily", "Weekly"], horizontal=True)
    if freq == "Daily":
        corr = correlation_matrix(returns_daily, min_periods=250)
    else:
        weekly = prices.resample("W-FRI").last()
        corr = correlation_matrix(get_returns(weekly), min_periods=100)
    corr = corr.rename(index=name_of, columns=name_of)
    fig = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu_r", aspect="auto")
    st.plotly_chart(fig)
    st.caption("Markets close at different times, so same-day correlations between regions are "
               "understated. Switch to Weekly to reduce that distortion.")

# ---------- Tab 4 ----------
with tab4:
    f = d["fundamentals"].copy()
    f["ROE (%)"] = f["roe"] * 100
    f["Market cap (INR tn)"] = f["market_cap"] / 1e12
    st.dataframe(
        f[["name", "pe", "ROE (%)", "debt_to_equity", "equity_multiplier",
           "Market cap (INR tn)", "fiscal_year_end", "source"]].round(2),
        hide_index=True)

    c1, c2 = st.columns(2)
    c1.plotly_chart(px.bar(f, x="name", y="ROE (%)", title="Return on equity (%)"))
    c2.plotly_chart(px.bar(f[f["is_bank"] == 0], x="name", y="debt_to_equity",
                           title="Debt / equity (non-banks only)"))
    st.info("HDFC Bank is a bank, where deposits make debt-to-equity meaningless, so it is compared "
            "on equity multiplier instead and not ranked on leverage.")
    st.subheader("Ranking (from SQL)")
    st.dataframe(d["q5"], hide_index=True)

# ---------- Tab 5 ----------
with tab5:
    dq = d["dq"]
    if dq.empty:
        st.success("No data quality issues found.")
    else:
        c1, c2 = st.columns(2)
        c1.metric("Items flagged", len(dq))
        c2.metric("Still need review", int((dq["severity"] == "review").sum()))
        st.dataframe(dq.sort_values(["severity", "asset", "date"]), hide_index=True)
    st.caption("Checks: stale data, large daily moves, date gaps, flat prices. 'review' means a human "
               "needs to decide; 'explained' means matched to a known event.")