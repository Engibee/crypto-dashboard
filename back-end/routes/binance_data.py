from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from services.technical_analysis import calculate_indicators
from utils.binance_data import api_to_df

router = APIRouter()

@router.get("/data/{symbol}")
def get_symbol_data(symbol: str, days: int = Query(default=90)):
    df = calculate_indicators(symbol, days)
    return JSONResponse(content=df.to_dict(orient="records"))

@router.get("/raw-data/{symbol}")
def get_raw_symbol_data(symbol: str, days: int = Query(default=90)):
    df = api_to_df(symbol, days)
    return JSONResponse(content=df.to_dict(orient="records"))
