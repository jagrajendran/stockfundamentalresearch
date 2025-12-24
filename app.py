import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="NSE Fundamental Valuation Dashboard",
                   layout="wide")

NSE_STOCKS = [
    "TCS.NS", "INFY.NS", "HDFCBANK.NS", "RELIANCE.NS",
    "ICICIBANK.NS", "ITC.NS", "LT.NS", "SBIN.NS",
    "HINDUNILVR.NS", "BHARTIARTL.NS"
]

SECTOR_PE_AVG = 25   # Simple assumption (can enhance later)

# --------------------------------------------------
# DATA FETCH
# --------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_fundamentals(symbol):
    t = yf.Ticker(symbol)
    info = t.info

    return {
        "Stock": symbol.replace(".NS", ""),
        "PE": info.get("trailingPE"),
        "PB": info.get("priceToBook"),
        "ROE": info.get("returnOnEquity"),
        "DebtEquity": info.get("debtToEquity"),
        "MarketCap": info.get("marketCap"),
        "RevenueGrowth": info.get("revenueGrowth"),
        "ProfitMargins": info.get("profitMargins")
    }

@st.cache_data(ttl=86400)
def load_data():
    rows = []
    for s in NSE_STOCKS:
        try:
            rows.append(fetch_fundamentals(s))
        except:
            pass
    return pd.DataFrame(rows)

# --------------------------------------------------
# SCORING LOGIC
# --------------------------------------------------
def calculate_score(row):
    score = 0

    if row["PE"] and row["PE"] < SECTOR_PE_AVG:
        score += 2
    if row["PB"] and row["PB"] < 3:
        score += 1
    if row["ROE"] and row["ROE"] > 0.15:
        score += 2
    if row["DebtEquity"] and row["DebtEquity"] < 0.5:
        score += 1
    if row["RevenueGrowth"] and row["RevenueGrowth"] > 0.10:
        score += 2
    if row["ProfitMargins"] and row["ProfitMargins"] > 0.10:
        score += 1

    return score

def valuation_label(score):
    if score >= 7:
        return "Undervalued"
    elif score >= 4:
        return "Neutral"
    else:
        return "Overvalued"

# --------------------------------------------------
# MAIN
# --------------------------------------------------
st.title("📊 NSE Fundamental Valuation Dashboard")
st.caption("Rule-based fundamental valuation | Long-term investing")

df = load_data()

if df.empty:
    st.error("No data fetched.")
    st.stop()

df["Score"] = df.apply(calculate_score, axis=1)
df["Valuation"] = df["Score"].apply(valuation_label)

# --------------------------------------------------
# KPIs
# --------------------------------------------------
col1, col2, col3 = st.columns(3)

col1.metric("🟢 Undervalued",
             df[df["Valuation"] == "Undervalued"].shape[0])

col2.metric("🟡 Neutral",
             df[df["Valuation"] == "Neutral"].shape[0])

col3.metric("🔴 Overvalued",
             df[df["Valuation"] == "Overvalued"].shape[0])

# --------------------------------------------------
# PIE CHART
# --------------------------------------------------
fig = px.pie(df,
             names="Valuation",
             title="Valuation Distribution",
             hole=0.4)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# FILTERS
# --------------------------------------------------
st.subheader("🔎 Stock Screener")

valuation_filter = st.multiselect(
    "Select Valuation",
    options=df["Valuation"].unique(),
    default=df["Valuation"].unique()
)

filtered_df = df[df["Valuation"].isin(valuation_filter)]

# --------------------------------------------------
# TABLE
# --------------------------------------------------
st.dataframe(
    filtered_df.sort_values("Score", ascending=False),
    use_container_width=True
)

# --------------------------------------------------
# STOCK DETAIL VIEW
# --------------------------------------------------
st.subheader("📈 Stock Detail")

stock = st.selectbox("Select Stock", df["Stock"])

stock_row = df[df["Stock"] == stock].iloc[0]

metrics_df = pd.DataFrame({
    "Metric": ["PE", "PB", "ROE", "Debt/Equity", "Revenue Growth", "Profit Margin"],
    "Value": [
        stock_row["PE"],
        stock_row["PB"],
        stock_row["ROE"],
        stock_row["DebtEquity"],
        stock_row["RevenueGrowth"],
        stock_row["ProfitMargins"]
    ]
})

st.table(metrics_df)

st.success(f"**Valuation:** {stock_row['Valuation']} | **Score:** {stock_row['Score']}")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.caption("⚠️ Educational purpose only. Not financial advice.")
