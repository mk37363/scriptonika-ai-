from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Грузим .env явно (на случай, если systemd не подхватил)
load_dotenv("/opt/skriptonika/ops/.env")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
JWT_SECRET = os.getenv("JWT_SECRET")

if not ADMIN_EMAIL or not ADMIN_PASSWORD or not JWT_SECRET:
    print("WARNING: ADMIN_EMAIL/ADMIN_PASSWORD/JWT_SECRET not set from .env")

import hmac, hashlib, base64, json, time

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _sign(msg: bytes) -> str:
    return _b64(hmac.new(JWT_SECRET.encode(), msg, hashlib.sha256).digest())

def make_jwt(sub: str, ttl=3600) -> str:
    header = _b64(json.dumps({"alg":"HS256","typ":"JWT"}).encode())
    payload = _b64(json.dumps({"sub":sub,"exp":int(time.time())+ttl}).encode())
    sig = _sign(f"{header}.{payload}".encode())
    return f"{header}.{payload}.{sig}"

router = APIRouter()

class LoginIn(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(payload: LoginIn):
    # Простая сверка с .env (без БД)
    if payload.email == ADMIN_EMAIL and payload.password == ADMIN_PASSWORD:
        return {"token": make_jwt(payload.email)}
    raise HTTPException(401, "bad credentials")
