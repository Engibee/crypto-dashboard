from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from utils.binance_data import api_to_df
from services.technical_analysis import calculate_indicators
router = APIRouter()

@router.get("/data/{symbol}")
def get_symbol_data(symbol: str, days: int = Query(default=90)):
    df = calculate_indicators(symbol, days)
    return JSONResponse(content=df.to_dict(orient="records"))
