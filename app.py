import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

st.set_page_config(page_title="Ultimate Portfolio Dashboard", page_icon="📈", layout="wide")

st.title("📈 Ultimate Live Portfolio & Technical Dashboard")
st.markdown("As3ar m3mola **Automatic** bylf 3la el souq w ygeb el data live mn 8er ay malft!")

# Define default tickers for Portfolio (EGX, Crypto, Gold, US Stocks)
default_tickers = {
    "CIB (EGX)": "COMI.CA",
    "TMG (EGX)": "TMGH.CA",
    "Edita (EGX)": "EFID.CA",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Gold": "GC=F",
    "Apple": "AAPL",
    "Microsoft": "MSFT"
}

st.sidebar.header("⚙️ Control Panel")
selected_name = st.sidebar.selectbox("E5tar el Asl aw el Sahm:", list(default_tickers.keys()))
ticker_symbol = default_tickers[selected_name]

# Fetch Data function with caching
@st.cache_data(ttl=300)
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="1mo")
        current_price = df['Close'].iloc[-1] if not df.empty else 0
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
        change = ((current_price - prev_price) / prev_price) * 100
        return current_price, change, df
    except Exception as e:
        return 0, 0, pd.DataFrame()

st.subheader(f"📊 Live Chart for: {selected_name} ({ticker_symbol})")

price, change, hist = get_stock_data(ticker_symbol)

col1, col2, col3 = st.columns(3)
col1.metric("El Se3r El 7aly", f"{price:,.2f}", f"{change:+.2f}%")
col2.metric("Last Updated", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
col3.metric("Status", "🟢 Live & Connected")

if not hist.empty:
    st.line_chart(hist['Close'])
else:
    st.warning("Mafe4 data mta7a ll symbol da 7alyan aw el souq m2fl.")

# Multi-stock overview table
st.markdown("---")
st.subheader("🌐 Global & EGX Market Watchlist")

watchlist_data = []
for name, sym in default_tickers.items():
    p, c, _ = get_stock_data(sym)
    watchlist_data.append({"Asset": name, "Ticker": sym, "Price": p, "Change (%)": c})

df_watch = pd.DataFrame(watchlist_data)
st.dataframe(df_watch, use_container_width=True)
