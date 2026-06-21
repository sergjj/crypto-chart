import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

st.set_page_config(layout="wide")

# Списки активов
CRYPTO_MAP = {'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'SOLANA': 'SOL-USD', 'BNB': 'BNB-USD'}
MACRO_MAP = {'USDT.D': 'USDT-USD', 'VIX': '^VIX', 'US10Y': '^TNX', 'BRENT': 'BZ=F'}
INTERVALS = {'1 час': '1h', '4 часа': '4h', '1 день': '1d'}

col1, col2, col3 = st.columns(3)
crypto_sel = col1.selectbox("Крипто:", list(CRYPTO_MAP.keys()))
macro_sel = col2.selectbox("Макро:", list(MACRO_MAP.keys()))
int_sel = col3.selectbox("Таймфрейм:", list(INTERVALS.keys()))

# Настройка MA
ma_input = st.sidebar.text_input("Периоды MA (через запятую)", "20,50,200")
ma_periods = [int(p.strip()) for p in ma_input.split(',')]

@st.cache_data(ttl=300)
def get_data(ticker, interval):
    return yf.download(ticker, period="1mo", interval=interval)

# Загружаем данные отдельно для каждого (чтобы были O, H, L, C)
crypto_df = get_data(CRYPTO_MAP[crypto_sel], INTERVALS[int_sel])
macro_df = get_data(MACRO_MAP[macro_sel], INTERVALS[int_sel])

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Свечи (теперь с Open/High/Low/Close)
fig.add_trace(go.Candlestick(x=crypto_df.index, open=crypto_df['Open'], 
                             high=crypto_df['High'], low=crypto_df['Low'], 
                             close=crypto_df['Close'], name=crypto_sel), secondary_y=False)

# Скользящие средние
for p in ma_periods:
    ma = crypto_df['Close'].rolling(window=p).mean()
    fig.add_trace(go.Scatter(x=crypto_df.index, y=ma, name=f'MA {p}', line=dict(width=1)), secondary_y=False)

# Макро-линия
fig.add_trace(go.Scatter(x=macro_df.index, y=macro_df['Close'], name=macro_sel, 
                         line=dict(color='yellow', width=1.5)), secondary_y=True)

fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False)
# Включаем панель управления обратно
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
