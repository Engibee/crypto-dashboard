import os

# API Configuration
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "your-secret-key-here")

# CORS Configuration
ALLOWED_ORIGINS = [
    "https://crypto-dashboard-nine-kohl.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
]

CORS_ORIGINS = ["http://localhost:5173","https://crypto-dashboard-nine-kohl.vercel.app"]

# Binance Configuration
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")