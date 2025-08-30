import pandas as pd

def calculate_rsi_wilder(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff()

    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    avg_gain = avg_gain.shift(1).combine(gain, lambda prev, cur: (prev * (period - 1) + cur) / period)
    avg_loss = avg_loss.shift(1).combine(loss, lambda prev, cur: (prev * (period - 1) + cur) / period)

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi
