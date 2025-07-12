from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from websocket import websocket_endpoint, raw_data_websocket_endpoint
from routes.binance_data import router as binance_router
from fastapi.middleware.cors import CORSMiddleware
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173/","https://crypto-dashboard-nine-kohl.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/data")
async def ws_data(websocket: WebSocket):
    try:
        await websocket_endpoint(websocket)
    except WebSocketDisconnect:
        # This is expected behavior when clients disconnect
        logger.info("Client disconnected from WebSocket")
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Unexpected error in WebSocket handler: {str(e)}")

@app.websocket("/ws/raw-data")
async def ws_raw_data(websocket: WebSocket):
    try:
        await raw_data_websocket_endpoint(websocket)
    except WebSocketDisconnect:
        # This is expected behavior when clients disconnect
        logger.info("Client disconnected from raw data WebSocket")
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Unexpected error in raw data WebSocket handler: {str(e)}")

app.include_router(binance_router, prefix="/api")
