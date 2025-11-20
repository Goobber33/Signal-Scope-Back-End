from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import os

from ..database import get_database
from ..schemas import UserCreate, UserLogin, UserResponse, Token
from ..auth.utils import (
    get_password_hash, verify_password,
    create_access_token
)

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()

# ---------------------------------------------------------
# OPTIONS HANDLERS - Handle preflight requests without DB dependency
# ---------------------------------------------------------
def get_allowed_origins():
    """Get allowed origins from environment or use defaults"""
    raw_origins = os.getenv("CORS_ORIGINS")
    if raw_origins:
        return [o.strip() for o in raw_origins.split(",") if o.strip()]
    return [
        "http://localhost:5173",
        "http://localhost:5174",
        "https://signal-scope-psi.vercel.app",
    ]

@router.options("/register")
async def options_register(request: Request):
    """Handle OPTIONS preflight for /register - no dependencies to avoid 500 errors"""
    origin = request.headers.get("origin")
    allowed_origins = get_allowed_origins()
    
    if origin and origin in allowed_origins:
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600",
            }
        )
    return Response(status_code=200)

@router.options("/login")
async def options_login(request: Request):
    """Handle OPTIONS preflight for /login - no dependencies to avoid 500 errors"""
    origin = request.headers.get("origin")
    allowed_origins = get_allowed_origins()
    
    if origin and origin in allowed_origins:
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600",
            }
        )
    return Response(status_code=200)

# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------
@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(user.password)

    doc = {
        "email": user.email,
        "password_hash": hashed,
        "name": user.name,
        "created_at": datetime.utcnow(),
    }

    result = await db.users.insert_one(doc)
    uid = str(result.inserted_id)

    token = create_access_token({"sub": uid})

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse(_id=uid, **user.dict(), created_at=doc["created_at"])
    )

# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncIOMotorDatabase = Depends(get_database)):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    uid = str(db_user["_id"])
    db_user["_id"] = uid  # Convert ObjectId → str

    token = create_access_token({"sub": uid})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse(**db_user),
    }
