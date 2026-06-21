import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

st.set_page_config(layout="wide")

# Конфигурация активов
CRYPTO_MAP = {'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'SOLANA': 'SOL-USD', 'BNB': 'BNB-USD'}
MACRO_MAP = {'USDT.D': 'USDT-USD', 'VIX': '^VIX', 'US10Y': '^TNX', 'BRENT': 'BZ=F'}
INTERVALS = {'1 час': '1h', '4 часа': '4h', '1 день': '1d', '1 неделя': '1wk'}

# Интерфейс
col1, col2, col3 = st.columns(3)
crypto_sel = col1.selectbox("Крипто:", list(CRYPTO_MAP.keys()))
macro_sel = col2.selectbox("Макро:", list(MACRO_MAP.keys()))
int_sel = col3.selectbox("Таймфрейм:", list(INTERVALS.keys()))

# Загрузка данных
@st.cache_data(ttl=300)
def get_data(c_tick, m_tick, interval):
    # Загружаем за 1 месяц, чтобы данные были плотными
    df = yf.download([c_tick, m_tick], period="1mo", interval=interval)['Close']
    return df.ffill() # Заполняем пропуски, чтобы убрать разрывы (как в TradingView)

data = get_data(CRYPTO_MAP[crypto_sel], MACRO_MAP[macro_sel], INTERVALS[int_sel])

# Создаем фигуру с двумя осями Y
fig = make_subplots(specs=[[{"secondary_y": True}]])

# 1. Свечи крипты (левая ось)
fig.add_trace(go.Candlestick(x=data.index, open=data[CRYPTO_MAP[crypto_sel]], 
                             high=data[CRYPTO_MAP[crypto_sel]], low=data[CRYPTO_MAP[crypto_sel]], 
                             close=data[CRYPTO_MAP[crypto_sel]], name=crypto_sel), secondary_y=False)

# 2. Линия макро (правая ось)
fig.add_trace(go.Scatter(x=data.index, y=data[MACRO_MAP[macro_sel]], name=macro_sel, 
                         line=dict(color='red', width=1.5)), secondary_y=True)

# Настройки оформления (убираем лишнее)
fig.update_layout(template="plotly_dark", height=700, showlegend=True,
                  xaxis_rangeslider_visible=False)
# Отключаем кнопки зума в modebar
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
