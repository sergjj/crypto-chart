import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("Pro Trading Terminal (Spot & Macro)")

# Конфигурация активов
CRYPTO_MAP = {
    'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'SOLANA': 'SOL-USD', 
    'BNB': 'BNB-USD', 'AVAX': 'AVAX-USD', 'RENDER': 'RENDER-USD', 
    'TAO': 'TAO-USD', 'HYPE': 'HYPE32196-USD'
}
MACRO_MAP = {
    'USD.T': 'USDT-USD', 'VIX': '^VIX', 'US10Y': '^TNX', 
    'BRENT': 'BZ=F', 'GOLD': 'GC=F'
}

# Интерфейс выбора
col1, col2 = st.columns(2)
crypto_sel = col1.selectbox("Крипто-актив:", list(CRYPTO_MAP.keys()))
macro_sel = col2.selectbox("Макро-индикатор:", list(MACRO_MAP.keys()))

# Настройка MA
ma_input = st.sidebar.text_input("Периоды MA (через запятую)", "20,50,200")
ma_periods = [int(p.strip()) for p in ma_input.split(',')]

@st.cache_data(ttl=3600)
def fetch_data(tickers):
    return yf.download(tickers, period="6mo", interval="1d")['Close']

# Загрузка
data = fetch_data([CRYPTO_MAP[crypto_sel], MACRO_MAP[macro_sel]])

# Создание графиков (2 ряда)
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                    row_heights=[0.7, 0.3])

# 1. Свечной график для крипты
fig.add_trace(go.Candlestick(x=data.index, open=data[CRYPTO_MAP[crypto_sel]], 
                             high=data[CRYPTO_MAP[crypto_sel]], low=data[CRYPTO_MAP[crypto_sel]], 
                             close=data[CRYPTO_MAP[crypto_sel]], name=crypto_sel), row=1, col=1)

# Добавляем MA
for p in ma_periods:
    ma = data[CRYPTO_MAP[crypto_sel]].rolling(window=p).mean()
    fig.add_trace(go.Scatter(x=data.index, y=ma, name=f'MA {p}'), row=1, col=1)

# 2. График для макро
fig.add_trace(go.Scatter(x=data.index, y=data[MACRO_MAP[macro_sel]], name=macro_sel, line=dict(color='red')), row=2, col=1)

fig.update_layout(xaxis_rangeslider_visible=False, height=800, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)
