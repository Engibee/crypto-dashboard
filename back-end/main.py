from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from utils.binance_data import api_to_df
from services.technical_analysis import calculate_indicators
from routes.binance_data import router as binance_router
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from services.live_data import start_ws_in_background, add_connection, remove_connection, SYMBOLS
from threading import Thread
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_ws_in_background(SYMBOLS)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://crypto-dashboard-nine-kohl.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_ORIGINS = [
    "https://crypto-dashboard-nine-kohl.vercel.app",
    "http://localhost:5173",
]

@app.middleware("http")
async def block_unauthorized_origins(request: Request, call_next):
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")

    # Permite apenas se a origem OU referer forem confiáveis
    if origin and not any(origin.startswith(o) for o in ALLOWED_ORIGINS):
        return JSONResponse(status_code=403, content={"detail": "Access denied"})
    if referer and not any(referer.startswith(o) for o in ALLOWED_ORIGINS):
        return JSONResponse(status_code=403, content={"detail": "Access denied"})

    return await call_next(request)

@app.get("/")
def home():
    return {"message": "API is online!"} # Aqui você pode retornar o que quiser, como uma página HTML ou um JSON com dados. Não se esqueça de atualizar o front-end para lidar com o retorno.

@app.get("/api/symbols")
def get_available_symbols():
    return {"symbols": SYMBOLS}

@app.websocket("/ws/data")
async def websocket_data_endpoint(websocket: WebSocket, ticker: str = Query("BTCUSDT")):
    await websocket.accept()
    
    # Extract symbol from ticker (remove USDT suffix)
    symbol = ticker.replace("USDT", "")
    add_connection(websocket, symbol, "data")
    
    logger.info(f"WebSocket connection established for {symbol} technical analysis data")

    try:
        while True:
            await asyncio.sleep(60)  # Keep connection alive
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for {symbol} technical analysis data")
    except asyncio.CancelledError:
        # This happens during server shutdown - it's normal
        logger.info(f"WebSocket cancelled for {symbol} (server shutdown)")
    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}")
    finally:
        remove_connection(websocket)

@app.websocket("/ws/raw-data")
async def websocket_raw_data_endpoint(websocket: WebSocket, ticker: str = Query("BTCUSDT")):
    await websocket.accept()
    
    # Extract symbol from ticker (remove USDT suffix)
    symbol = ticker.replace("USDT", "")
    add_connection(websocket, symbol, "raw-data")
    
    logger.info(f"WebSocket connection established for {symbol} raw data")

    try:
        while True:
            await asyncio.sleep(60)  # Keep connection alive
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for {symbol} raw data")
    except asyncio.CancelledError:
        # This happens during server shutdown - it's normal
        logger.info(f"WebSocket cancelled for {symbol} (server shutdown)")
    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}")
    finally:
        remove_connection(websocket)

@app.websocket("/ws/live-price")
async def websocket_live_price_endpoint(websocket: WebSocket, ticker: str = Query("BTCUSDT")):
    await websocket.accept()
    
    # Extract symbol from ticker (remove USDT suffix)
    symbol = ticker.replace("USDT", "")
    add_connection(websocket, symbol, "live-price")
    
    logger.info(f"WebSocket connection established for {symbol} live price")

    try:
        while True:
            await asyncio.sleep(60)  # Keep connection alive
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for {symbol} live price")
    except asyncio.CancelledError:
        # This happens during server shutdown - it's normal
        logger.info(f"WebSocket cancelled for {symbol} (server shutdown)")
    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}")
    finally:
        remove_connection(websocket)

@app.get("/api/raw-data")
async def get_raw_data():
    try:
        df = api_to_df()
        return JSONResponse(content=df.to_dict(orient="records"))
    except Exception as e:
        logger.error(f"Erro ao gerar dados brutos da API: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar os dados brutos")

app.include_router(binance_router, prefix="/api")
