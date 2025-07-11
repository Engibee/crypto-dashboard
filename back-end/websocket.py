import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from services.technical_analysis import calculate_indicators
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection established")

        ticker = websocket.query_params.get("ticker", "BTCUSDT")
        days = int(websocket.query_params.get("days", 90))
        
        logger.info(f"Streaming data for {ticker}, days={days}")

        # Send data in a loop until client disconnects
        while True:
            try:
                df = calculate_indicators(ticker, days)
                json_data = df.reset_index().to_dict(orient="records")
                await websocket.send_text(json.dumps(json_data))
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error processing data: {str(e)}")
                # Continue the loop even if there's an error processing data
                await asyncio.sleep(1)
                
    except WebSocketDisconnect:
        # This is normal - client disconnected
        logger.info(f"WebSocket client disconnected")
    except Exception as e:
        # Log any other unexpected errors
        logger.error(f"WebSocket error: {str(e)}")
