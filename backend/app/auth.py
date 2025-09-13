import os, time, hmac, hashlib, base64, json
from fastapi import HTTPException, Header

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
JWT_SECRET = os.getenv("JWT_SECRET")

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _sign(msg: bytes) -> str:
    return _b64(hmac.new(JWT_SECRET.encode(), msg, hashlib.sha256).digest())

def make_jwt(sub: str, ttl=3600) -> str:
    header = _b64(json.dumps({"alg":"HS256","typ":"JWT"}).encode())
    payload = _b64(json.dumps({"sub":sub, "exp": int(time.time())+ttl}).encode())
    sig = _sign(f"{header}.{payload}".encode())
    return f"{header}.{payload}.{sig}"

def verify_jwt(token: str) -> dict:
    try:
        h,p,s = token.split(".")
        if _sign(f"{h}.{p}".encode()) != s:
            raise ValueError("bad signature")
        payload = json.loads(base64.urlsafe_b64decode(p + "=="))
        if payload["exp"] < time.time():
            raise ValueError("expired")
        return payload
    except Exception as e:
        raise HTTPException(401, f"invalid token: {e}")

def admin_login(email: str, password: str) -> str:
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        return make_jwt(email)
    raise HTTPException(401, "bad credentials")

def require_auth(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "no token")
    payload = verify_jwt(authorization.split(" ",1)[1])
    return payload["sub"]
