from contextlib import asynccontextmanager
from fastapi import FastAPI
from services.live_data import start_ws_in_background, SYMBOLS

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_ws_in_background(SYMBOLS)
    yield