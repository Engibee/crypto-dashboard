from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.lifespan import lifespan
from middleware.security import block_unauthorized_origins
from routes.binance_data import router as binance_router
from routes.websocket import router as websocket_router
from routes.api import router as api_router
from config.settings import CORS_ORIGINS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(block_unauthorized_origins)

# Include routers
app.include_router(api_router)
app.include_router(websocket_router)
app.include_router(binance_router, prefix="/api")
