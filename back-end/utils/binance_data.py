from binance.client import Client
from functools import lru_cache
from dotenv import load_dotenv
from utils.date import get_date_days_ago
import pandas as pd
import os
from datetime import datetime, timedelta
import time

load_dotenv()

# Chaves da API (opcional para dados públicos)
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

# Cache with timestamp for invalidation
_cache_timestamps = {}
_cache_data = {}
CACHE_DURATION = 3600  # 1 hour in seconds

def _get_cache_key(symbol, days):
    return f"{symbol}_{days}"

def _is_cache_valid(cache_key):
    if cache_key not in _cache_timestamps:
        return False
    return time.time() - _cache_timestamps[cache_key] < CACHE_DURATION

# Pegar histórico de candles (OHLCV) — exemplo: BTC/USDT
def api_to_df(symbol, days: int | None = None):
    cache_key = _get_cache_key(symbol, days)

    # Check if we have valid cached data
    if _is_cache_valid(cache_key) and cache_key in _cache_data:
        return _cache_data[cache_key].copy()  # Return copy to avoid mutations

    # Fetch fresh data
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

    # Cache the processed data
    _cache_data[cache_key] = df.copy()
    _cache_timestamps[cache_key] = time.time()

    # LINE BELOW ALLOWS TO SAVE DATA LOCALLY
    #df.to_csv("data/BTCUSDT.csv", index=False)

    return df

def clear_cache(symbol=None, days=None):
    """Clear cache for specific symbol/days or all cache"""
    if symbol and days:
        cache_key = _get_cache_key(symbol, days)
        _cache_data.pop(cache_key, None)
        _cache_timestamps.pop(cache_key, None)
    else:
        _cache_data.clear()
        _cache_timestamps.clear()

def get_cache_info():
    """Get cache statistics"""
    return {
        "cached_items": len(_cache_data),
        "cache_keys": list(_cache_data.keys()),
        "oldest_cache": min(_cache_timestamps.values()) if _cache_timestamps else None,
        "newest_cache": max(_cache_timestamps.values()) if _cache_timestamps else None
    }

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

