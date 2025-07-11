import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from services.technical_analysis import calculate_indicators
import json
import logging
from starlette.websockets import WebSocketState

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
        connection_active = True
        while connection_active:
            try:
                # Calculate indicators
                df = calculate_indicators(ticker, days)
                json_data = df.reset_index().to_dict(orient="records")
                
                # Try to send data, but catch specific exceptions
                try:
                    await websocket.send_text(json.dumps(json_data))
                except RuntimeError as e:
                    if "Cannot call \"send\" once a close message has been sent" in str(e):
                        logger.info("WebSocket connection is closed, stopping data stream")
                        connection_active = False
                        break
                    else:
                        # Re-raise if it's a different RuntimeError
                        raise
                except WebSocketDisconnect:
                    logger.info("Client disconnected during send operation")
                    connection_active = False
                    break
                
                # Wait before sending next update
                await asyncio.sleep(1)
                
            except WebSocketDisconnect:
                # Client disconnected, exit the loop
                logger.info(f"WebSocket client disconnected")
                connection_active = False
                break
            except Exception as e:
                # Log any other unexpected errors
                logger.error(f"Error processing data: {str(e)}")
                # Short delay before retry
                await asyncio.sleep(1)
                
    except WebSocketDisconnect:
        # This is normal - client disconnected during connection setup
        logger.info(f"WebSocket client disconnected during setup")
    except Exception as e:
        # Log any other unexpected errors
        logger.error(f"WebSocket error: {str(e)}")
