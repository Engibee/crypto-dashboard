import asyncio
import threading
import websockets
import json
import time
from starlette.websockets import WebSocketState

price_store = {"btcusdt": 0, "ethusdt": 0, "adausdt": 0}
ws_task = None

# Rate limiting - track last send time per connection
last_send_times = {}  # {websocket: timestamp}
SEND_INTERVAL = 1.0  # 1 second minimum between sends

SYMBOLS = [
    {"symbol": "BTC","stream": "btcusdt@trade", "label": "Bitcoin"},
    {"symbol": "ETH","stream": "ethusdt@trade", "label": "Ethereum"},
    {"symbol": "ADA","stream": "adausdt@trade", "label": "Cardano"},
]

# Store connections with their requested symbols
connections = {}  # {websocket: {"symbol": "BTC", "endpoint": "data"}}

async def binance_ws(symbols):
    from services.technical_analysis import calculate_indicators
    from utils.binance_data import api_to_df
    
    url = build_multiplexed_url(symbols)
    async with websockets.connect(url) as ws:
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            stream = data["stream"]
            payload = data["data"]
            symbol = payload["s"].lower()

            price = float(payload["p"])  # último preço
            price_store[symbol] = price

            # Clean up dead connections before sending data
            await cleanup_dead_connections()

            # Send data only to connections that requested this symbol
            symbol_upper = symbol.replace("usdt", "").upper()  # Convert btcusdt -> BTC
            current_time = time.time()
            
            for conn, conn_info in list(connections.items()):
                try:
                    # Check if connection is still alive
                    if conn.client_state == WebSocketState.DISCONNECTED:
                        connections.pop(conn, None)
                        last_send_times.pop(conn, None)
                        continue
                    
                    # Rate limiting: only send if enough time has passed
                    if conn in last_send_times:
                        time_since_last_send = current_time - last_send_times[conn]
                        if time_since_last_send < SEND_INTERVAL:
                            continue  # Skip this update
                    
                    # Check if this connection wants this symbol
                    if conn_info["symbol"] == symbol_upper:
                        if conn_info["endpoint"] == "data":
                            df = calculate_indicators(symbol.upper())  # Use full symbol like BTCUSDT
                            await conn.send_text(df.to_json(orient="records"))
                            last_send_times[conn] = current_time
                        elif conn_info["endpoint"] == "raw-data":
                            df = api_to_df(symbol.upper())  # Use full symbol like BTCUSDT
                            await conn.send_text(df.to_json(orient="records"))
                            last_send_times[conn] = current_time
                        elif conn_info["endpoint"] == "live-price":
                            # Send just the live price data
                            price_data = {
                                "symbol": symbol_upper,
                                "price": price,
                                "timestamp": current_time
                            }
                            await conn.send_text(json.dumps(price_data))
                            last_send_times[conn] = current_time
                            
                except Exception as e:
                    # Remove broken connections
                    print(f"Removing broken connection: {e}")
                    connections.pop(conn, None)
                    last_send_times.pop(conn, None)

def build_multiplexed_url(symbols: list[dict]) -> str:
    streams = "/".join(item["stream"] for item in symbols)
    return f"wss://stream.binance.com:9443/stream?streams={streams}"

def start_ws_in_background(symbols):
    def run():
        asyncio.run(binance_ws(symbols))
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

async def cleanup_dead_connections():
    """Remove connections that are no longer active"""
    dead_connections = []
    for conn, conn_info in connections.items():
        try:
            if conn.client_state == WebSocketState.DISCONNECTED:
                dead_connections.append(conn)
        except Exception:
            dead_connections.append(conn)
    
    for conn in dead_connections:
        connections.pop(conn, None)
        last_send_times.pop(conn, None)
        print(f"Cleaned up dead connection. Total connections: {len(connections)}")

def add_connection(websocket, symbol, endpoint):
    """Add a connection with its requested symbol and endpoint"""
    # Clean up any existing dead connections first
    dead_connections = []
    for conn in connections.keys():
        try:
            if conn.client_state == WebSocketState.DISCONNECTED:
                dead_connections.append(conn)
        except Exception:
            dead_connections.append(conn)
    
    for conn in dead_connections:
        connections.pop(conn, None)
        last_send_times.pop(conn, None)
    
    connections[websocket] = {"symbol": symbol, "endpoint": endpoint}
    last_send_times[websocket] = 0  # Initialize to allow immediate first send
    print(f"Added connection for {symbol} ({endpoint}). Total connections: {len(connections)}")

def remove_connection(websocket):
    """Remove a connection"""
    if websocket in connections:
        conn_info = connections.pop(websocket)
        last_send_times.pop(websocket, None)
        print(f"Removed connection for {conn_info['symbol']} ({conn_info['endpoint']}). Total connections: {len(connections)}")
    else:
        print("Attempted to remove connection that doesn't exist")
