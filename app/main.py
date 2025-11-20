import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .database import connect_to_mongo, close_mongo_connection
from .routers import auth, towers, reports, analytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SignalScope API", version="1.0.0")

# CORS origins - Railway-friendly parsing
raw_origins = os.getenv("CORS_ORIGINS")
if raw_origins:
    origins = [o.strip() for o in raw_origins.split(",")]
else:
    # Default origins if CORS_ORIGINS not set
    origins = [
        "http://localhost:5173",
        "http://localhost:5174",
        "https://signal-scope-psi.vercel.app",
    ]

logger.info(f"[CORS] Allowing origins: {origins}")

# Simple request logger to verify requests reach the app
class SimpleLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"[REQUEST] {request.method} {request.url.path} | Origin: {request.headers.get('origin', 'none')}")
        response = await call_next(request)
        logger.info(f"[RESPONSE] {request.method} {request.url.path} | Status: {response.status_code}")
        return response

app.add_middleware(SimpleLoggerMiddleware)

# CORS middleware - MUST be added before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB lifecycle
@app.on_event("startup")
async def startup():
    logger.info("[STARTUP] SignalScope API Starting...")
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()

# Routers
app.include_router(auth.router)
app.include_router(towers.router)
app.include_router(reports.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {"status": "ok", "service": "SignalScope API"}
