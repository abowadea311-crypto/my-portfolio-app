import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

st.set_page_config(page_title="Ultimate Portfolio & Technical Dashboard", page_icon="📈", layout="wide")

st.title("📈 Ultimate Live Portfolio & Technical Analysis Dashboard")
st.markdown("Dashboard متكاملة لكل أسهم السوق المصري، الأمريكي، الكริبتو، والذهب مع تحليل فني ومحفظة متقدمة!")

# قائمة موسعة تشمل أسهم السوق الأمريكي (NVDA, INTC, AAPL, MSFT) والمصري والبتكوين
default_tickers = {
    "Nvidia (US)": "NVDA",
    "Intel (US)": "INTC",
    "Apple (US)": "AAPL",
    "Microsoft (US)": "MSFT",
    "CIB (EGX)": "COMI.CA",
    "TMG (EGX)": "TMGH.CA",
    "Edita (EGX)": "EFID.CA",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Gold": "GC=F"
}

st.sidebar.header("⚙️ Control & Settings")
selected_name = st.sidebar.selectbox("إختار الأصل (Asset):", list(default_tickers.keys()))
ticker_symbol = default_tickers[selected_name]

# Fetch data function with caching
@st.cache_data(ttl=300)
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="6mo")
        if df.empty:
            return None
        return df
    except Exception as e:
        return None

df = get_stock_data(ticker_symbol)

if df is not None and not df.empty:
    auto_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2] if len(df) > 1 else auto_price
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠️ تحكم يدوي في السعر")
    use_manual = st.sidebar.checkbox("تفعيل السعر اليدوي (Manual Price)", value=False)
    
    if use_manual:
        current_price = st.sidebar.number_input("ادخل السعر الحالي يدوياً:", value=float(auto_price), step=0.1)
        price_status = "✍️ يدوي (Manual Override)"
    else:
        current_price = auto_price
        price_status = "🟢 تلقائي لايف (Live Auto)"

    change_pct = ((current_price - prev_price) / prev_price) * 100

    # حساب المؤشرات الفنية (Technical Indicators)
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    current_rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
    sma20 = df['SMA_20'].iloc[-1] if not pd.isna(df['SMA_20'].iloc[-1]) else current_price
    sma50 = df['SMA_50'].iloc[-1] if not pd.isna(df['SMA_50'].iloc[-1]) else current_price

    recent_df = df.tail(30)
    support = recent_df['Low'].min()
    resistance = recent_df['High'].max()

    tab1, tab2, tab3 = st.tabs(["📊 التحليل الفني والتوقعات", "💰 إدارة المحفظة والقيم", "🌐 مراقبة السوق (Watchlist)"])

    with tab1:
        st.subheader(f"🔍 التحليل الفني والإشارات لـ: {selected_name} ({ticker_symbol})")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("السعر الحالي", f"{current_price:,.2f}", f"{change_pct:+.2f}%")
        col2.metric("حالة التسعير", price_status, f"آخر سحب: {datetime.datetime.now().strftime('%H:%M:%S')}")
        col3.metric("الدعم القريب (Support)", f"{support:,.2f}")
        col4.metric("المقاومة القريبة (Resistance)", f"{resistance:,.2f}")

        st.markdown("### 🤖 إشارات السوق والتوقعات (Technical Outlook)")
        signal = "محايد (Neutral)"
        signal_color = "orange"
        if current_price > sma20 and sma20 > sma50:
            signal = "صاعد إيجابي (Bullish) 🚀"
            signal_color = "green"
        elif current_price < sma20 and sma20 < sma50:
            signal = "هابط سلبي (Bearish) 🔻"
            signal_color = "red"

        st.markdown(f"**الاتجاه العام الحالي (Trend):** :{signal_color}[{signal}]")
        
        if current_rsi < 30:
            st.info("💡 **تنبيه (فرصة ارتداد):** السهم في منطقة تشبع بيعي (Oversold).")
        elif current_rsi > 70:
            st.warning("⚠️ **تنبيه (تشبع شراء):** السهم في منطقة تشبع شرائي (Overbought).")
        else:
            st.success("✅ **الوضع مستقر:** الحركة السعرية ضمن النطاق الطبيعي.")

        st.markdown("---")
        st.subheader("📉 الشارت التاريخي مع المتوسطات المتحركة (SMA)")
        st.line_chart(df[['Close', 'SMA_20', 'SMA_50']].tail(100))

    with tab2:
        st.subheader("💼 حسابات المحفظة والقيم والأرباح (Portfolio Valuation)")
        
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            qty = st.number_input(f"الكمية المملوكة من {selected_name}:", min_value=0.0, value=100.0, step=10.0)
        with col_in2:
            avg_buy = st.number_input(f"متوسط سعر الشراء:", min_value=0.0, value=float(current_price * 0.95), step=0.1)

        total_value = qty * current_price
        total_cost = qty * avg_buy
        total_profit = total_value - total_cost
        profit_pct = ((total_profit / total_cost) * 100) if total_cost > 0 else 0

        pcol1, pcol2, pcol3, pcol4 = st.columns(4)
        pcol1.metric("إجمالي القيمة السوقية", f"{total_value:,.2f}")
        pcol2.metric("إجمالي التكلفة", f"{total_cost:,.2f}")
        pcol3.metric("صافي الربح / الخسارة", f"{total_profit:+,.2f}", f"{profit_pct:+.2f}%")
        pcol4.metric("السعر المستخدم", f"{current_price:,.2f}")

    with tab3:
        st.markdown("### 🌐 جدول متابعة السوق الشامل (Global & EGX Watchlist)")
        watchlist_data = []
        for name, sym in default_tickers.items():
            d = get_stock_data(sym)
            if d is not None and not d.empty:
                p = d['Close'].iloc[-1]
                pr = d['Close'].iloc[-2] if len(d) > 1 else p
                c = ((p - pr) / pr) * 100
                watchlist_data.append({"Asset": name, "Ticker": sym, "Price": round(p, 2), "Change (%)": round(c, 2)})
        
        if watchlist_data:
            st.dataframe(pd.DataFrame(watchlist_data), use_container_width=True)

else:
    st.error("عذراً، لا توجد بيانات متاحة لهذا الرمز حالياً.")
