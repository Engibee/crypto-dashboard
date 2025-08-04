from binance.client import Client
from functools import lru_cache
from dotenv import load_dotenv
from utils.date import get_date_days_ago
import pandas as pd
import os
from datetime import datetime, timedelta

load_dotenv()

# Chaves da API (opcional para dados públicos)
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

# Pegar histórico de candles (OHLCV) — exemplo: BTC/USDT
@lru_cache(maxsize=32)
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

    # LINE BELOW ALLOWS TO SAVE DATA LOCALLY
    #df.to_csv("data/BTCUSDT.csv", index=False)

    return df

@lru_cache(maxsize=32)
def get_today_stats(symbol):
    """Get today's OHLCV data - cached for 5 minutes"""
    try:
        # Get 24hr ticker statistics
        ticker = client.get_ticker(symbol=symbol)
        
        return {
            "symbol": symbol,
            "open": float(ticker['openPrice']),
            "high": float(ticker['highPrice']),
            "low": float(ticker['lowPrice']),
            "volume": float(ticker['volume']),
            "price_change": float(ticker['priceChange']),
            "price_change_percent": float(ticker['priceChangePercent']),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"Error fetching today's stats for {symbol}: {e}")
        return None

