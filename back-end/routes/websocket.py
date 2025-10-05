from fastapi import WebSocket, WebSocketDisconnect, Query, APIRouter
from services.live_data import add_connection, remove_connection
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/data")
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

@router.websocket("/ws/raw-data")
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

@router.websocket("/ws/live-price")
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