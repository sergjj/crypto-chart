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
# ЗАМЕНИТЕ ВАШ ТЕКУЩИЙ INTERVALS НА ЭТОТ:
INTERVALS = {
    '1ч': '1h', 
    '4ч': '4h', 
    '5ч': '5H', 
    '8ч': '8H', 
    '13ч': '13H', 
    '18ч': '18H', 
    '1д': '1D', 
    '3д': '3D', 
    '5д': '5D'
}

col1, col2 = st.columns([1, 1])
crypto_sel = col1.selectbox("Актив:", list(CRYPTO_MAP.keys()))
int_sel = col2.selectbox("Таймфрейм:", list(INTERVALS.keys()))

ma_input = st.sidebar.text_input("Периоды MA", "20,50,200")
ma_periods = [int(p.strip()) for p in ma_input.split(',')]

@st.cache_data(ttl=300)
def get_custom_data(symbol, interval):
    exchange = ccxt.okx()
    symbol = symbol.replace('/', '-')
    
    # Сначала всегда грузим часовые данные как базу
    bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=1000)
    df = pd.DataFrame(bars, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Timestamp', inplace=True)

    # Если интервал стандартный — возвращаем как есть
    if interval in ['5m', '15m', '30m', '1h', '4h', '1d']:
        return df.reset_index()

    # Если ваш "хитрый" интервал (например, '5H' — 5 часов)
    # Используем resample для группировки часовых свечей
    agg_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
    resampled_df = df.resample(interval).agg(agg_dict).dropna()
    
    return resampled_df.reset_index()

data = get_data(CRYPTO_MAP[crypto_sel], INTERVALS[int_sel])

# Отрисовка
fig = go.Figure()
fig.add_trace(go.Candlestick(x=data['Timestamp'], open=data['Open'], high=data['High'], 
                             low=data['Low'], close=data['Close'], name='Цена'))

for p in ma_periods:
    ma = data['Close'].rolling(window=p).mean()
    fig.add_trace(go.Scatter(x=data['Timestamp'], y=ma, name=f'MA {p}', line=dict(width=1.5)))

fig.update_layout(
    template="plotly_dark",
    height=750,
    xaxis_rangeslider_visible=False,
    yaxis=dict(side="right"),
    # Включаем "прицел" (Crosshair)
    hovermode="x unified", # Показывает все данные в одной подсказке
)

# Добавляем "шипы" (Spikes) для осей
fig.update_xaxes(
    showspikes=True,
    spikemode="across",
    spikesnap="cursor",
    spikecolor="gray",
    spikethickness=1,
    spikedash="dot"
)

fig.update_yaxes(
    showspikes=True,
    spikemode="across",
    spikesnap="cursor",
    spikecolor="gray",
    spikethickness=1,
    spikedash="dot"
)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
