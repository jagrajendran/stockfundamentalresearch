import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="NIFTY Fundamental Valuation Dashboard",
                   layout="wide")

SECTOR_PE_AVG = 25

# --------------------------------------------------
# NSE INDEX STOCK LISTS
# --------------------------------------------------
NIFTY_50 = [
    "ADANIENT.NS","ADANIPORTS.NS","APOLLOHOSP.NS","ASIANPAINT.NS","AXISBANK.NS",
    "BAJAJ-AUTO.NS","BAJFINANCE.NS","BAJAJFINSV.NS","BPCL.NS","BHARTIARTL.NS",
    "BRITANNIA.NS","CIPLA.NS","COALINDIA.NS","DIVISLAB.NS","DRREDDY.NS",
    "EICHERMOT.NS","GRASIM.NS","HCLTECH.NS","HDFCBANK.NS","HDFCLIFE.NS",
    "HEROMOTOCO.NS","HINDALCO.NS","HINDUNILVR.NS","ICICIBANK.NS","ITC.NS",
    "INDUSINDBK.NS","INFY.NS","JSWSTEEL.NS","KOTAKBANK.NS","LT.NS",
    "M&M.NS","MARUTI.NS","NTPC.NS","ONGC.NS","POWERGRID.NS",
    "RELIANCE.NS","SBIN.NS","SUNPHARMA.NS","TCS.NS","TATACONSUM.NS",
    "TATAMOTORS.NS","TATASTEEL.NS","TECHM.NS","TITAN.NS","ULTRACEMCO.NS",
    "UPL.NS","WIPRO.NS"
]

NIFTY_NEXT_50 = [
    "ABB.NS","ACC.NS","ADANIGREEN.NS","ADANITRANS.NS","AMBUJACEM.NS",
    "AUBANK.NS","BANDHANBNK.NS","BERGEPAINT.NS","BOSCHLTD.NS","CANBK.NS",
    "CHOLAFIN.NS","COLPAL.NS","DLF.NS","GAIL.NS","GODREJCP.NS",
    "HAVELLS.NS","ICICIPRULI.NS","IGL.NS","INDIGO.NS","JINDALSTEL.NS",
    "LICHSGFIN.NS","LUPIN.NS","MARICO.NS","MOTHERSUMI.NS","NMDC.NS",
    "OFSS.NS","PAGEIND.NS","PETRONET.NS","PIDILITIND.NS","PNB.NS",
    "SIEMENS.NS","SRF.NS","TORNTPHARM.NS","TVSMOTOR.NS","UBL.NS",
    "VEDL.NS","VOLTAS.NS","ZEEL.NS"
]

NIFTY_101_150 = [
    "ABFRL.NS","ALKEM.NS","ASHOKLEY.NS","ASTRAL.NS","ATUL.NS",
    "AUROPHARMA.NS","BATAINDIA.NS","BEL.NS","BHARATFORG.NS","BIRLACORPN.NS",
    "CESC.NS","COFORGE.NS","COROMANDEL.NS","CROMPTON.NS","DEEPAKNTR.NS",
    "ESCORTS.NS","EXIDEIND.NS","FEDERALBNK.NS","GLENMARK.NS","GNFC.NS",
    "HDFCAMC.NS","IDFCFIRSTB.NS","IPCALAB.NS","IRCTC.NS","JUBLFOOD.NS",
    "KANSAINER.NS","LALPATHLAB.NS","LTTS.NS","MFSL.NS","MPHASIS.NS",
    "NAM-INDIA.NS","OBEROIRLTY.NS","POLYCAB.NS","PRESTIGE.NS","RAMCOCEM.NS",
    "SAIL.NS","SUNTV.NS","TRENT.NS","UNITDSPR.NS","ZYDUSLIFE.NS"
]

NIFTY_151_250 = [
    "AARTIIND.NS","ABBOTINDIA.NS","ACE.NS","ADANIPOWER.NS","AFFLE.NS",
    "AJANTPHARM.NS","ALKYLAMINE.NS","AMARAJABAT.NS","ANGELONE.NS","APARINDS.NS",
    "APLLTD.NS","BALAMINES.NS","BALKRISIND.NS","BASF.NS","BAYERCROP.NS",
    "BDL.NS","BSOFT.NS","CAMS.NS","CANFINHOME.NS","CARBORUNIV.NS",
    "CDSL.NS","CENTRALBK.NS","CERA.NS","CHALET.NS","CLEAN.NS",
    "CONCOR.NS","CREDITACC.NS","CYIENT.NS","DATAPATTNS.NS","DCMSHRIRAM.NS",
    "DELTACORP.NS","DEVYANI.NS","DIXON.NS","EASEMYTRIP.NS","ELGIEQUIP.NS",
    "ENDURANCE.NS","EQUITASBNK.NS","FINEORG.NS","FORTIS.NS","FSL.NS",
    "GESHIP.NS","GILLETTE.NS","GMMPFAUDLR.NS","GRANULES.NS","GUJGASLTD.NS",
    "HAL.NS","HAPPSTMNDS.NS","HFCL.NS","IEX.NS","INDIAMART.NS",
    "INTELLECT.NS","IRB.NS","IRFC.NS","JBCHEPHARM.NS","JSL.NS",
    "KEC.NS","KEI.NS","KPITTECH.NS","LAXMIMACH.NS","MAHLOG.NS",
    "MAHSCOOTER.NS","MCX.NS","METROPOLIS.NS","MGL.NS","NATCOPHARM.NS",
    "NAVINFLUOR.NS","NBCC.NS","NESCO.NS","NIITLTD.NS","NUVOCO.NS",
    "PFIZER.NS","PERSISTENT.NS","POLYMED.NS","RAIN.NS","RBLBANK.NS",
    "RECLTD.NS","REDINGTON.NS","ROUTE.NS","SANOFI.NS","SCHAEFFLER.NS",
    "SONATSOFTW.NS","SPANDANA.NS","STAR.NS","SUNDRMFAST.NS","SUPREMEIND.NS",
    "SYNGENE.NS","TATAELXSI.NS","TATACHEM.NS","TATAPOWER.NS","TCIEXP.NS",
    "THERMAX.NS","TIINDIA.NS","TORNTPOWER.NS","TRIDENT.NS","UCOBANK.NS",
    "UNIONBANK.NS","VINATIORGA.NS","WHIRLPOOL.NS","ZENSARTECH.NS"
]
INDEX_MAP = {
    "NIFTY 50": NIFTY_50,
    "NIFTY 51–100": NIFTY_NEXT_50,
    "NIFTY 101–150": NIFTY_101_150,
    "NIFTY 151–250": NIFTY_151_250
}

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
        "RevenueGrowth": info.get("revenueGrowth"),
        "ProfitMargin": info.get("profitMargins")
    }

@st.cache_data(ttl=86400)
def load_index_data(symbols):
    data = []
    for s in symbols:
        try:
            data.append(fetch_fundamentals(s))
        except:
            pass
    return pd.DataFrame(data)

# --------------------------------------------------
# SCORING
# --------------------------------------------------
def score_stock(row):
    score = 0
    if row["PE"] and row["PE"] < SECTOR_PE_AVG: score += 2
    if row["PB"] and row["PB"] < 3: score += 1
    if row["ROE"] and row["ROE"] > 0.15: score += 2
    if row["DebtEquity"] and row["DebtEquity"] < 0.5: score += 1
    if row["RevenueGrowth"] and row["RevenueGrowth"] > 0.10: score += 2
    if row["ProfitMargin"] and row["ProfitMargin"] > 0.10: score += 1
    return score

def valuation(score):
    if score >= 7: return "Undervalued"
    elif score >= 4: return "Neutral"
    return "Overvalued"

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("📊 NIFTY Fundamental Valuation Dashboard")

index_choice = st.sidebar.selectbox(
    "Select Index",
    list(INDEX_MAP.keys())
)

df = load_index_data(INDEX_MAP[index_choice])
df["Score"] = df.apply(score_stock, axis=1)
df["Valuation"] = df["Score"].apply(valuation)

# KPIs
c1, c2, c3 = st.columns(3)
c1.metric("🟢 Undervalued", (df["Valuation"] == "Undervalued").sum())
c2.metric("🟡 Neutral", (df["Valuation"] == "Neutral").sum())
c3.metric("🔴 Overvalued", (df["Valuation"] == "Overvalued").sum())

# Pie
fig = px.pie(df, names="Valuation", hole=0.4, title="Valuation Distribution")
st.plotly_chart(fig, use_container_width=True)

# Table
st.subheader("🔎 Stock Screener")
st.dataframe(df.sort_values("Score", ascending=False), use_container_width=True)

# Stock Detail
st.subheader("📈 Stock Details")
stock = st.selectbox("Select Stock", df["Stock"])
row = df[df["Stock"] == stock].iloc[0]

st.write(row)
st.success(f"Valuation: **{row['Valuation']}** | Score: **{row['Score']}**")

st.caption("⚠️ Educational purpose only. Not investment advice.")
