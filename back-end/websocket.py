import asyncio
from fastapi import WebSocket
from services.technical_analysis import calculate_indicators
import json

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    ticker = websocket.query_params.get("ticker", "BTCUSDT")
    days = int(websocket.query_params.get("days", 90))

    while True:
        df = calculate_indicators(ticker, days)

        json_data = df.reset_index().to_dict(orient="records")

        await websocket.send_text(json.dumps(json_data))

        await asyncio.sleep(1)