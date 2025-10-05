# Crypto Dashboard API

A FastAPI-based cryptocurrency data API that provides real-time price data, technical analysis indicators, and market statistics using Binance WebSocket and REST APIs.

## Features

- **Real-time Data**: Live cryptocurrency prices via WebSocket connections
- **Technical Analysis**: SMA, EMA, RSI, MACD indicators
- **Market Statistics**: Daily OHLCV data and 24hr statistics
- **Multiple Endpoints**: REST and WebSocket support
- **Rate Limiting**: Optimized data delivery (1 update per second)
- **Security**: Origin validation and API key authentication
- **Caching**: LRU cache for efficient data retrieval

## Tech Stack

- **FastAPI**: Modern Python web framework
- **WebSockets**: Real-time bidirectional communication
- **Pandas**: Data manipulation and analysis
- **python-binance**: Binance API integration
- **Uvicorn**: ASGI server

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd back-end
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment Setup**
Create a `.env` file in the root directory:
```env
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
API_SECRET_KEY=your_secret_api_key
```

4. **Run the server**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### REST Endpoints

#### Get Technical Analysis Data
```http
GET /api/data/{symbol}?days=90
```
Returns technical indicators (SMA, EMA, RSI, MACD) for the specified symbol.

**Parameters:**
- `symbol`: Cryptocurrency symbol (e.g., BTCUSDT)
- `days`: Number of days of historical data (default: 90)

**Response:**
```json
[
  {
    "timestamp": "2024-01-01 00:00:00",
    "Open": 42000.0,
    "High": 43000.0,
    "Low": 41000.0,
    "Close": 42500.0,
    "Volume": 1000.0,
    "SMA": 42250.0,
    "EMA": 42300.0,
    "RSI": 65.5,
    "MACD": 150.2,
    "MACD_Signal": 140.1,
    "Signal": 1
  }
]
```

#### Get Raw Price Data
```http
GET /api/raw-data/{symbol}?days=90
```
Returns raw OHLCV data without technical indicators.

#### Get Today's Statistics
```http
GET /api/today-stats/{symbol}
```
Returns 24hr statistics for the symbol.

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "open": 42000.0,
  "high": 43500.0,
  "low": 41000.0,
  "volume": 15000.0,
  "price_change": 500.0,
  "price_change_percent": 1.19,
  "timestamp": "2024-01-01 12:00:00"
}
```

#### Get Available Symbols
```http
GET /api/symbols
```
Returns list of supported cryptocurrency symbols.

### WebSocket Endpoints

#### Technical Analysis Data Stream
```
ws://localhost:8000/ws/data?ticker=BTCUSDT&days=90
```
Streams real-time technical analysis data.

#### Raw Data Stream
```
ws://localhost:8000/ws/raw-data?ticker=BTCUSDT&days=90
```
Streams real-time raw price data.

#### Live Price Stream
```
ws://localhost:8000/ws/live-price?ticker=BTCUSDT
```
Streams real-time price updates.

**Response Format:**
```json
{
  "symbol": "BTC",
  "price": 42500.0,
  "timestamp": 1704110400
}
```

## Security

### Origin Validation
The API validates requests based on:
- Origin header
- Referer header
- User-agent (blocks direct browser access)

### Allowed Origins
Configure allowed origins in `main.py`:
```python
ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
    "http://localhost:5173",
    "http://localhost:3000"
]
```

### API Key Authentication
Include the API key in request headers:
```http
x-api-key: your-secret-api-key
```

## Rate Limiting

WebSocket connections are rate-limited to 1 update per second per connection to optimize performance and reduce bandwidth usage.

## Caching

- **Historical Data**: Cached using `@lru_cache` (maxsize=32)
- **Today's Statistics**: Cached to reduce API calls to Binance
- **Cache Duration**: Automatic invalidation based on data freshness

## Supported Cryptocurrencies

- Bitcoin (BTC)
- Ethereum (ETH)
- Cardano (ADA)

Additional symbols can be added in `services/live_data.py`:
```python
SYMBOLS = [
    {"symbol": "BTC", "stream": "btcusdt@trade", "label": "Bitcoin"},
    {"symbol": "ETH", "stream": "ethusdt@trade", "label": "Ethereum"},
    # Add more symbols here
]
```

## Technical Indicators

### Simple Moving Average (SMA)
Average price over a specified period (default: 14 days).

### Exponential Moving Average (EMA)
Weighted average giving more importance to recent prices (default: 14 days).

### Relative Strength Index (RSI)
Momentum oscillator measuring speed and change of price movements (default: 14 days).

### MACD (Moving Average Convergence Divergence)
Trend-following momentum indicator showing relationship between two moving averages.
- Fast EMA: 12 days
- Slow EMA: 26 days
- Signal Line: 9 days

## Error Handling

The API includes comprehensive error handling:
- WebSocket connection management
- Dead connection cleanup
- Graceful fallbacks
- Detailed error logging

## Deployment

### Environment Variables
Set the following environment variables for production:
```env
BINANCE_API_KEY=your_production_api_key
BINANCE_API_SECRET=your_production_api_secret
API_SECRET_KEY=your_production_secret_key
```

### CORS Configuration
Update CORS settings for production domains:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-production-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Development

### Running Tests
```bash
python test_binance.py
```

### Code Structure
```
back-end/
├── main.py                 # FastAPI application and routes
├── routes/
│   └── binance_data.py     # API route handlers
├── services/
│   ├── technical_analysis.py  # Technical indicator calculations
│   └── live_data.py        # WebSocket data streaming
├── utils/
│   ├── binance_data.py     # Binance API integration
│   └── date.py             # Date utilities
└── requirements.txt        # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on the repository or contact the development team.