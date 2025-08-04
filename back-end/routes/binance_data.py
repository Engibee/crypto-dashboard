from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from services.technical_analysis import calculate_indicators
from utils.binance_data import api_to_df, get_today_stats

router = APIRouter()

@router.get("/data/{symbol}")
def get_symbol_data(symbol: str, days: int = Query(default=90)):
    df = calculate_indicators(symbol, days)
    return JSONResponse(content=df.to_dict(orient="records"))

@router.get("/raw-data/{symbol}")
def get_raw_symbol_data(symbol: str, days: int = Query(default=90)):
    df = api_to_df(symbol, days)
    return JSONResponse(content=df.to_dict(orient="records"))

@router.get("/today-stats/{symbol}")
def get_today_stats_endpoint(symbol: str):
    """Get today's OHLCV statistics for a symbol"""
    stats = get_today_stats(symbol)
    if stats:
        return JSONResponse(content=stats)
    else:
        return JSONResponse(content={"error": "Failed to fetch today's stats"}, status_code=500)
