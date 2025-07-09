from binance.client import Client
from dotenv import load_dotenv
from utils.date import get_date_days_ago
import pandas as pd
import os

load_dotenv()

# Chaves da API (opcional para dados públicos)
API_KEY = os.getenv("BINANCE_API_KEY") or "sua_api_key_aqui"
API_SECRET = os.getenv("BINANCE_API_SECRET") or "sua_api_secret_aqui"

client = Client(API_KEY, API_SECRET)

# Pegar histórico de candles (OHLCV) — exemplo: BTC/USDT
def api_to_df(symbol, days: int | None = None):
    klines = client.get_historical_klines(
        symbol=symbol,
        interval=Client.KLINE_INTERVAL_1DAY,
        start_str=get_date_days_ago(days),
    )

    df = pd.DataFrame(klines, columns=[
        "timestamp", "Open", "High", "Low", "Close", "Volume",
        "Close_time", "Quote_asset_volume", "Number_of_trades",
        "Taker_buy_base_vol", "Taker_buy_quote_vol", "Ignore"
    ])

    df = df.drop(columns=["Close_time", "Taker_buy_base_vol", "Taker_buy_quote_vol", "Ignore"])

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df["timestamp"] = df["timestamp"].dt.strftime('%Y-%m-%d %H:%M:%S')
    df[["Open", "High", "Low", "Close", "Volume"]] = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
    # Usar direto com backtester
    print(df.tail())

    # OU salvar como CSV local
    #df.to_csv("data/BTCUSDT.csv", index=False)

    return df
