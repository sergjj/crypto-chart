import streamlit as st
import plotly.graph_objects as go
import ccxt
import pandas as pd

st.set_page_config(layout="wide")
st.title("Crypto Terminal Pro")

# Конфигурация
CRYPTO_MAP = {'BTC': 'BTC/USDT', 'ETH': 'ETH/USDT', 'SOLANA': 'SOL/USDT', 'BNB': 'BNB/USDT'}
INTERVALS = {'1 час': '1h', '4 часа': '4h', '1 день': '1d', '1 неделя': '1w'}

# Интерфейс
col1, col2 = st.columns([1, 1])
crypto_sel = col1.selectbox("Актив:", list(CRYPTO_MAP.keys()))
int_sel = col2.selectbox("Таймфрейм:", list(INTERVALS.keys()))

ma_input = st.sidebar.text_input("Периоды MA (через запятую)", "20,50,200")
ma_periods = [int(p.strip()) for p in ma_input.split(',')]

# Загрузка через Binance
@st.cache_data(ttl=300)
def get_binance_data(symbol, interval):
    # Меняем биржу на OKX, она работает в облаке без проблем
    exchange = ccxt.okx() 
    # У OKX тикеры пишутся через дефис, как и у нас (BTC-USDT)
    symbol = symbol.replace('/', '-') 
    bars = exchange.fetch_ohlcv(symbol, timeframe=interval, limit=100)
    df = pd.DataFrame(bars, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    return df

data = get_binance_data(CRYPTO_MAP[crypto_sel], INTERVALS[int_sel])

# Отрисовка
fig = go.Figure()

# Свечи
fig.add_trace(go.Candlestick(x=data['Timestamp'], open=data['Open'], high=data['High'], 
                             low=data['Low'], close=data['Close'], name='Цена'))

# Скользящие средние
for p in ma_periods:
    ma = data['Close'].rolling(window=p).mean()
    fig.add_trace(go.Scatter(x=data['Timestamp'], y=ma, name=f'MA {p}', line=dict(width=1.5)))

fig.update_layout(template="plotly_dark", height=750, 
                  xaxis_rangeslider_visible=False,
                  margin=dict(l=10, r=10, t=30, b=30))

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
