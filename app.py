import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# --------------------------------------------------
# APP CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="NIFTY Fundamental Valuation Dashboard",
    layout="wide"
)

SECTOR_PE_AVG = 25

# --------------------------------------------------
# INDEX STOCK LISTS (50–250)
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
    "ABB.NS","ACC.NS","ADANIGREEN.NS","AMBUJACEM.NS","AUBANK.NS","BANDHANBNK.NS",
    "BERGEPAINT.NS","BOSCHLTD.NS","CANBK.NS","CHOLAFIN.NS","COLPAL.NS","DLF.NS",
    "GAIL.NS","GODREJCP.NS","HAVELLS.NS","ICICIPRULI.NS","IGL.NS","INDIGO.NS",
    "JINDALSTEL.NS","LICHSGFIN.NS","LUPIN.NS","MARICO.NS","NMDC.NS","OFSS.NS",
    "PAGEIND.NS","PETRONET.NS","PIDILITIND.NS","PNB.NS","SIEMENS.NS","SRF.NS",
    "TORNTPHARM.NS","TVSMOTOR.NS","UBL.NS","VEDL.NS","VOLTAS.NS","ZEEL.NS"
]

NIFTY_101_150 = [
    "ABFRL.NS","ALKEM.NS","ASHOKLEY.NS","ASTRAL.NS","AUROPHARMA.NS","BATAINDIA.NS",
    "BEL.NS","BHARATFORG.NS","COFORGE.NS","COROMANDEL.NS","CROMPTON.NS",
    "DEEPAKNTR.NS","ESCORTS.NS","EXIDEIND.NS","FEDERALBNK.NS","HDFCAMC.NS",
    "IDFCFIRSTB.NS","IRCTC.NS","JUBLFOOD.NS","KANSAINER.NS","LTTS.NS","MPHASIS.NS",
    "OBEROIRLTY.NS","POLYCAB.NS","RAMCOCEM.NS","SAIL.NS","SUNTV.NS","TRENT.NS",
    "UNITDSPR.NS","ZYDUSLIFE.NS"
]

NIFTY_151_250 = [
    "AARTIIND.NS","ABBOTINDIA.NS","ACE.NS","ADANIPOWER.NS","AFFLE.NS",
    "AJANTPHARM.NS","ALKYLAMINE.NS","ANGELONE.NS","APARINDS.NS","BALAMINES.NS",
    "BALKRISIND.NS","BAYERCROP.NS","BDL.NS","CAMS.NS","CANFINHOME.NS","CDSL.NS",
    "CERA.NS","CHALET.NS","CONCOR.NS","CREDITACC.NS","CYIENT.NS","DCMSHRIRAM.NS",
    "DIXON.NS","EASEMYTRIP.NS","ELGIEQUIP.NS","ENDURANCE.NS","FINEORG.NS",
    "FORTIS.NS","GESHIP.NS","GMMPFAUDLR.NS","GRANULES.NS","HAL.NS",
    "HAPPSTMNDS.NS","HFCL.NS","IEX.NS","INDIAMART.NS","INTELLECT.NS","IRFC.NS",
    "KEI.NS","KPITTECH.NS","LAXMIMACH.NS","MCX.NS","METROPOLIS.NS","NAVINFLUOR.NS",
    "NBCC.NS","PERSISTENT.NS","RECLTD.NS","ROUTE.NS","SCHAEFFLER.NS",
    "SONATSOFTW.NS","SUNDRMFAST.NS","SUPREMEIND.NS","SYNGENE.NS","TATAELXSI.NS",
    "TATAPOWER.NS","THERMAX.NS","TORNTPOWER.NS","VINATIORGA.NS","WHIRLPOOL.NS"
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
        "Stock": symbol.replace(".NS",""),
        "Symbol": symbol,
        "Sector": info.get("sector"),
        "CMP": info.get("currentPrice"),
        "52W High": info.get("fiftyTwoWeekHigh"),
        "52W Low": info.get("fiftyTwoWeekLow"),
        "Dividend Yield %": (info.get("dividendYield") or 0) * 100,
        "Face Value": info.get("faceValue"),
        "PE": info.get("trailingPE"),
        "PB": info.get("priceToBook"),
        "ROE": info.get("returnOnEquity"),
        "DebtEquity": info.get("debtToEquity"),
        "RevenueGrowth": info.get("revenueGrowth"),
        "ProfitMargin": info.get("profitMargins")
    }

@st.cache_data(ttl=86400)
def load_data(symbols):
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
def score_stock(r):
    s = 0
    if r["PE"] and r["PE"] < SECTOR_PE_AVG: s += 2
    if r["PB"] and r["PB"] < 3: s += 1
    if r["ROE"] and r["ROE"] > 0.15: s += 2
    if r["DebtEquity"] and r["DebtEquity"] < 0.5: s += 1
    if r["RevenueGrowth"] and r["RevenueGrowth"] > 0.10: s += 2
    if r["ProfitMargin"] and r["ProfitMargin"] > 0.10: s += 1
    return s

def valuation_label(score):
    if score >= 7: return "Undervalued"
    if score >= 4: return "Neutral"
    return "Overvalued"

# --------------------------------------------------
# FINANCIALS
# --------------------------------------------------
@st.cache_data(ttl=86400)
def quarterly_financials(symbol):
    t = yf.Ticker(symbol)
    df = t.quarterly_financials.T.reset_index()
    df.rename(columns={"index":"Quarter"}, inplace=True)

    df["Sales"] = df["Total Revenue"]
    df["Operating Profit"] = df["Operating Income"]
    df["Net Profit"] = df["Net Income"]

    df["OPM %"] = (df["Operating Profit"]/df["Sales"])*100
    df["Net Margin %"] = (df["Net Profit"]/df["Sales"])*100
    df["Sales YoY %"] = df["Sales"].pct_change(4)*100
    df["Profit YoY %"] = df["Net Profit"].pct_change(4)*100

    return df.sort_values("Quarter", ascending=False)

@st.cache_data(ttl=86400)
def annual_financials(symbol):
    t = yf.Ticker(symbol)
    df = t.financials.T.reset_index()
    df.rename(columns={"index":"Year"}, inplace=True)

    df["Sales"] = df["Total Revenue"]
    df["Operating Profit"] = df["Operating Income"]
    df["Net Profit"] = df["Net Income"]

    df["OPM %"] = (df["Operating Profit"]/df["Sales"])*100
    df["Net Margin %"] = (df["Net Profit"]/df["Sales"])*100

    return df.sort_values("Year", ascending=False)

# --------------------------------------------------
# PDF EXPORT
# --------------------------------------------------
def generate_pdf(stock, row):
    file = f"{stock}_report.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph(f"<b>{stock} Fundamental Report</b>", styles["Title"]))
    content.append(Paragraph(f"CMP: ₹{row['CMP']}", styles["Normal"]))
    content.append(Paragraph(f"Valuation: {row['Valuation']} (Score {row['Score']})", styles["Normal"]))
    content.append(Paragraph(f"PE: {row['PE']} | ROE: {row['ROE']}", styles["Normal"]))

    doc.build(content)
    return file

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("📊 NIFTY Fundamental Valuation Dashboard")

index_choice = st.sidebar.selectbox("Select Index", INDEX_MAP.keys())

df = load_data(INDEX_MAP[index_choice])
df["Score"] = df.apply(score_stock, axis=1)
df["Valuation"] = df["Score"].apply(valuation_label)

# KPIs
c1,c2,c3 = st.columns(3)
c1.metric("🟢 Undervalued", (df["Valuation"]=="Undervalued").sum())
c2.metric("🟡 Neutral", (df["Valuation"]=="Neutral").sum())
c3.metric("🔴 Overvalued", (df["Valuation"]=="Overvalued").sum())

st.plotly_chart(px.pie(df, names="Valuation", hole=0.4), use_container_width=True)

st.subheader("🔎 Stock Screener")
st.dataframe(df.sort_values("Score", ascending=False), use_container_width=True)

st.subheader("📈 Stock Details")
stock = st.selectbox("Select Stock", df["Stock"])
row = df[df["Stock"]==stock].iloc[0]

k1,k2,k3,k4 = st.columns(4)
k1.metric("CMP", f"₹ {row['CMP']}")
k2.metric("52W High", f"₹ {row['52W High']}")
k3.metric("52W Low", f"₹ {row['52W Low']}")
k4.metric("Dividend Yield", f"{row['Dividend Yield %']:.2f}%")

st.success(f"Valuation: **{row['Valuation']}** | Score: **{row['Score']}**")

tab1,tab2,tab3 = st.tabs(["Quarterly Results","Annual Results","Peer Comparison"])

with tab1:
    st.dataframe(quarterly_financials(row["Symbol"]), use_container_width=True)

with tab2:
    st.dataframe(annual_financials(row["Symbol"]), use_container_width=True)

with tab3:
    peers = df[df["Sector"]==row["Sector"]][["Stock","CMP","PE","ROE","DebtEquity"]]
    st.dataframe(peers.sort_values("ROE", ascending=False), use_container_width=True)

if st.button("📄 Download PDF Report"):
    pdf = generate_pdf(stock, row)
    with open(pdf,"rb") as f:
        st.download_button("Download", f, file_name=pdf)

st.caption("⚠️ Educational purpose only. Not investment advice.")
