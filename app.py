import streamlit as st
import plotly.graph_objects as go
import ccxt
import pandas as pd

st.set_page_config(layout="wide")

# Расширенный список активов
CRYPTO_MAP = {
    'BTC': 'BTC/USDT', 'ETH': 'ETH/USDT', 'SOLANA': 'SOL/USDT', 'BNB': 'BNB/USDT',
    'AVAX': 'AVAX/USDT', 'RENDER': 'RENDER/USDT', 'TAO': 'TAO/USDT', 
    'XRP': 'XRP/USDT', 'LINK': 'LINK/USDT', 'NEAR': 'NEAR/USDT', 'DOGE': 'DOGE/USDT'
}

# Стандартные таймфреймы
INTERVALS = {'5м': '5m', '15м': '15m', '30м': '30m', '1ч': '1h', '4ч': '4h', '1д': '1d'}

col1, col2 = st.columns([1, 1])
crypto_sel = col1.selectbox("Актив:", list(CRYPTO_MAP.keys()))
int_sel = col2.selectbox("Таймфрейм:", list(INTERVALS.keys()))

ma_input = st.sidebar.text_input("Периоды MA", "20,50,200")
ma_periods = [int(p.strip()) for p in ma_input.split(',')]

@st.cache_data(ttl=300)
def get_data(symbol, interval):
    exchange = ccxt.okx() # Используем стабильный OKX
    symbol = symbol.replace('/', '-')
    # Увеличиваем лимит до 1000 для глубокого анализа
    bars = exchange.fetch_ohlcv(symbol, timeframe=interval, limit=1000)
    df = pd.DataFrame(bars, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    return df

data = get_data(CRYPTO_MAP[crypto_sel], INTERVALS[int_sel])

# Отрисовка
fig = go.Figure()
fig.add_trace(go.Candlestick(x=data['Timestamp'], open=data['Open'], high=data['High'], 
                             low=data['Low'], close=data['Close'], name='Цена'))

for p in ma_periods:
    ma = data['Close'].rolling(window=p).mean()
    fig.add_trace(go.Scatter(x=data['Timestamp'], y=ma, name=f'MA {p}', line=dict(width=1.5)))

fig.update_layout(template="plotly_dark", height=750, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
