import logging
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .database import connect_to_mongo, close_mongo_connection
from .routers import auth, towers, reports, analytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SignalScope API", version="1.0.0")

# CORS origins - supports comma-separated values from environment
raw_origins = os.getenv("CORS_ORIGINS")
logger.info(f"[CORS] CORS_ORIGINS env var: {raw_origins}")

if raw_origins:
    # Split by comma, strip whitespace, filter out empty strings
    origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
    logger.info(f"[CORS] Parsed origins from env: {origins}")
else:
    # Default origins if CORS_ORIGINS not set
    origins = [
        "http://localhost:5173",
        "http://localhost:5174",
        "https://signal-scope-psi.vercel.app",
    ]
    logger.info(f"[CORS] Using default origins: {origins}")

logger.info(f"[CORS] Final allowed origins: {origins}")

# CORS middleware - MUST be added FIRST, before any other middleware or routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Simple request logger to verify requests reach the app
class SimpleLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get('origin', 'none')
        logger.info(f"[REQUEST] {request.method} {request.url.path} | Origin: {origin}")
        response = await call_next(request)
        logger.info(f"[RESPONSE] {request.method} {request.url.path} | Status: {response.status_code} | Origin: {origin}")
        return response

app.add_middleware(SimpleLoggerMiddleware)

# Force CORS headers on all responses
# This runs AFTER CORS middleware to ensure headers are always present
@app.middleware("http")
async def force_cors_headers(request: Request, call_next):
    """Force CORS headers on all responses to ensure they're always present"""
    response = await call_next(request)
    origin = request.headers.get("origin")
    
    if origin and origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
        # Explicitly list common headers instead of "*" when credentials are used
        response.headers["Access-Control-Allow-Headers"] = "content-type, authorization, accept, origin, x-requested-with, cache-control, pragma"
    
    return response

# Global OPTIONS handler for preflight requests
# Must be defined BEFORE routers to catch all OPTIONS requests
@app.options("/{full_path:path}")
async def global_options_handler(request: Request, full_path: str):
    """Global OPTIONS handler for preflight requests - handles CORS properly"""
    origin = request.headers.get("origin")
    requested_headers = request.headers.get("access-control-request-headers", "")
    requested_method = request.headers.get("access-control-request-method", "")
    
    logger.info(f"[OPTIONS] Global handler for path: {full_path} | Origin: {origin} | Requested headers: {requested_headers} | Requested method: {requested_method}")
    
    # Return response with explicit CORS headers
    if origin and origin in origins:
        # When credentials are allowed, we can't use "*" for headers
        # Instead, echo back the requested headers or use explicit list
        allowed_headers = requested_headers if requested_headers else "content-type, authorization, accept, origin, x-requested-with"
        
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD",
                "Access-Control-Allow-Headers": allowed_headers,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600",
            }
        )
    
    # Return empty response if origin not allowed (CORS middleware will handle it)
    return Response(status_code=200)

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
