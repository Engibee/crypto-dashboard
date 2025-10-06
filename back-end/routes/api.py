from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from utils.binance_data import api_to_df, get_cache_info, clear_cache
from services.live_data import SYMBOLS, price_store, volume_store
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
def home():
    return {"message": "API is online!"}

@router.get("/api/symbols")
def get_available_symbols():
    return {"symbols": SYMBOLS}

@router.get("/api/symbols/validate/{symbol}")
def validate_symbol(symbol: str):
    """Validate if a symbol is supported"""
    symbol_upper = symbol.upper()
    is_valid = any(s["symbol"] == symbol_upper for s in SYMBOLS)
    return {
        "symbol": symbol_upper,
        "valid": is_valid,
        "available_symbols": [s["symbol"] for s in SYMBOLS]
    }

@router.get("/api/raw-data")
async def get_raw_data():
    try:
        df = api_to_df()
        return JSONResponse(content=df.to_dict(orient="records"))
    except Exception as e:
        logger.error(f"Erro ao gerar dados brutos da API: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar os dados brutos")

@router.get("/api/health")
async def health_check():
    """Health check endpoint with cache and live data status"""
    try:
        cache_info = get_cache_info()
        live_prices = {k: v for k, v in price_store.items() if v > 0}
        live_volumes = {k: v for k, v in volume_store.items() if v > 0}

        return JSONResponse(content={
            "status": "healthy",
            "cache": cache_info,
            "live_prices": live_prices,
            "live_volumes": live_volumes,
            "symbols": SYMBOLS
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.post("/api/cache/clear")
async def clear_cache_endpoint(symbol: str = None, days: int = None):
    """Clear cache for optimization or troubleshooting"""
    try:
        clear_cache(symbol, days)
        return JSONResponse(content={
            "message": f"Cache cleared for {symbol if symbol else 'all symbols'}"
        })
    except Exception as e:
        logger.error(f"Cache clear failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Cache clear failed")
