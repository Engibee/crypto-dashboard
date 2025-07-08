from utils.binance_data import api_to_df
from services.technical_analysis import calculate_indicators

print(calculate_indicators('BTCUSDT', days=90))