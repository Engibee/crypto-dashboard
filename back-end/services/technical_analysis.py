import pandas as pd
import numpy as np
from utils.binance_data import api_to_df
from services.live_data import price_store

def calculate_indicators(ticker, days=30, sma_period=14, ema_period=14, rsi_period=14, macd_fast=12, macd_slow=26, macd_signal=9):
    df = api_to_df(ticker, days) #Cached

    price = price_store.get(ticker.lower())

    if price >= df.loc[df.index[-1], "High"]:
        df.loc[df.index[-1], "High"] = price

    if price <= df.loc[df.index[-1], "Low"]:
        df.loc[df.index[-1], "Low"] = price

    df.loc[df.index[-1], "Close"] = price

    # SMA (Simple Moving Average)
    df["SMA"] = df["Close"].rolling(window=sma_period).mean()

    # EMA (Exponential Moving Average)
    df["EMA"] = df["Close"].ewm(span=ema_period, adjust=False).mean()

    # RSI (Relative Strength Index)
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD (Moving Average Convergence Divergence)
    ema_fast = df["Close"].ewm(span=macd_fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=macd_slow, adjust=False).mean()
    df["MACD"] = ema_fast - ema_slow
    df["MACD_Signal"] = df["MACD"].ewm(span=macd_signal, adjust=False).mean()

    # Signal (1 se SMA > EMA, senão 0)
    df["Signal"] = (df["SMA"] > df["EMA"]).astype(int)

    # Apenas as colunas desejadas
    return df[["timestamp","SMA", "EMA", "RSI", "MACD", "MACD_Signal", "Signal"]].iloc[[-1]].replace([np.nan, np.inf, -np.inf], None)
