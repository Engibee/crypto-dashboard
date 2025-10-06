import pandas as pd
import numpy as np
from utils.binance_data import api_to_df
from utils.data_loader import calculate_rsi_wilder
from services.live_data import price_store, volume_store

def calculate_indicators(ticker, days=30, sma_period=14, ema_period=14, rsi_period=14, macd_fast=12, macd_slow=26, macd_signal=9):
    df = api_to_df(ticker, days) #Cached

    price = price_store.get(ticker.lower())
    live_volume = volume_store.get(ticker.lower(), 0)

    # Only update if we have a valid live price
    if price and price > 0:
        # Validate price is reasonable (within 20% of last close)
        last_close = df.loc[df.index[-1], "Close"]
        if abs(price - last_close) / last_close <= 0.2:  # 20% threshold
            if price >= df.loc[df.index[-1], "High"]:
                df.loc[df.index[-1], "High"] = price

            if price <= df.loc[df.index[-1], "Low"]:
                df.loc[df.index[-1], "Low"] = price

            df.loc[df.index[-1], "Close"] = price

            # Update today's volume with accumulated live volume
            if live_volume > 0:
                # Add live volume to the cached volume for today
                cached_volume = df.loc[df.index[-1], "Volume"]
                df.loc[df.index[-1], "Volume"] = cached_volume + live_volume
        else:
            # Log suspicious price but don't update
            print(f"Warning: Suspicious price {price} for {ticker}, last close was {last_close}")
    else:
        # No live price available, use cached data as-is
        print(f"No live price available for {ticker}, using cached data")

    # SMA (Simple Moving Average)
    df["SMA"] = df["Close"].rolling(window=sma_period).mean()

    # EMA (Exponential Moving Average)
    df["EMA"] = df["Close"].ewm(span=ema_period, adjust=False).mean()

    # RSI (Relative Strength Index)
    
    df["RSI"] = calculate_rsi_wilder(df["Close"], rsi_period)

    # MACD (Moving Average Convergence Divergence)
    ema_fast = df["Close"].ewm(span=macd_fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=macd_slow, adjust=False).mean()
    df["MACD"] = ema_fast - ema_slow
    df["MACD_Signal"] = df["MACD"].ewm(span=macd_signal, adjust=False).mean()

    # Signal (1 se SMA > EMA, senão 0)
    df["Signal"] = (df["SMA"] > df["EMA"]).astype(int)

    # Apenas as colunas desejadas
    return df[["timestamp","SMA", "EMA", "RSI", "MACD", "MACD_Signal", "Signal"]].iloc[[-1]].replace([np.nan, np.inf, -np.inf], None)
