from fastapi import FastAPI, WebSocket
from websocket import websocket_endpoint
from routes.binance_data import router as binance_router
from fastapi.middleware.cors import CORSMiddleware

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
    await websocket_endpoint(websocket)

app.include_router(binance_router, prefix="/api")