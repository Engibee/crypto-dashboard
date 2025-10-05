from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from utils.binance_data import api_to_df
from services.live_data import SYMBOLS
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
def home():
    return {"message": "API is online!"}

@router.get("/api/symbols")
def get_available_symbols():
    return {"symbols": SYMBOLS}

@router.get("/api/raw-data")
async def get_raw_data():
    try:
        df = api_to_df()
        return JSONResponse(content=df.to_dict(orient="records"))
    except Exception as e:
        logger.error(f"Erro ao gerar dados brutos da API: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar os dados brutos")
