import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(layout="wide")
DATA_FILE = "crypto_data.csv"
TICKERS = {'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'SOL': 'SOL-USD', 'AVAX': 'AVAX-USD', 'USDT.D': 'USDT.D'}

@st.cache_data
def load_data(update=False):
    if os.path.exists(DATA_FILE) and not update:
        return pd.read_csv(DATA_FILE, index_col='Date', parse_dates=True)
    
    data = yf.download(list(TICKERS.values()), period="1y", interval="1d")['Close']
    data.columns = TICKERS.keys()
    data.to_csv(DATA_FILE)
    return data

# Интерфейс
st.title("Crypto Analysis Dashboard")
ma_period = st.sidebar.slider("Период скользящей средней (MA)", 5, 200, 20)
if st.sidebar.button("Обновить данные"):
    df = load_data(update=True)
else:
    df = load_data()

# Построение графика
fig = go.Figure()

# Добавление активов
for asset in ['BTC', 'ETH', 'SOL', 'AVAX']:
    fig.add_trace(go.Scatter(x=df.index, y=df[asset], name=asset))
    # MA
    ma = df[asset].rolling(window=ma_period).mean()
    fig.add_trace(go.Scatter(x=df.index, y=ma, name=f'{asset} MA{ma_period}', line=dict(dash='dot')))

# Добавление USDT.D на вторичную ось (наложение)
fig.add_trace(go.Scatter(
    x=df.index, y=df['USDT.D'], name='USDT.D', 
    yaxis="y2", line=dict(color='red', width=2)
))

fig.update_layout(
    title="Сравнение цен и доминирования USDT",
    yaxis=dict(title="Цена USD"),
    yaxis2=dict(title="USDT.D (%)", overlaying="y", side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

st.plotly_chart(fig, use_container_width=True)
