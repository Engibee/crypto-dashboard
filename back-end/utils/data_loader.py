import pandas as pd

def calculate_rsi_wilder(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff()

    # ganhos e perdas
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # SMA inicial dos primeiros `period` valores
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # inicializa listas
    rsi = pd.Series(index=prices.index, dtype=float)

    # primeira média é a SMA
    avg_gain.iloc[period] = gain.iloc[:period+1].mean()
    avg_loss.iloc[period] = loss.iloc[:period+1].mean()

    # iteração manual (estilo Wilder)
    for i in range(period+1, len(prices)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period

        rs = avg_gain.iloc[i] / avg_loss.iloc[i] if avg_loss.iloc[i] != 0 else 0
        rsi.iloc[i] = 100 - (100 / (1 + rs))

    return rsi
