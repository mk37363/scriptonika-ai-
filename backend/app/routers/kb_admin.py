from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Optional, Literal
import os, json, time, base64, hmac, hashlib

# Хранилище в файле (без БД)
KB_DIR = "/opt/skriptonika/kb"
KB_PATH = os.path.join(KB_DIR, "kb.json")
os.makedirs(KB_DIR, exist_ok=True)
if not os.path.exists(KB_PATH):
    with open(KB_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)

# Верификация JWT (тот же секрет, что в /api/admin/login)
JWT_SECRET = os.getenv("JWT_SECRET")

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _sign(msg: bytes) -> str:
    return _b64(hmac.new(JWT_SECRET.encode(), msg, hashlib.sha256).digest())

def verify_jwt(token: str) -> dict:
    try:
        h, p, s = token.split(".")
        if _sign(f"{h}.{p}".encode()) != s:
            raise ValueError("bad signature")
        payload = json.loads(base64.urlsafe_b64decode(p + "=="))
        if payload["exp"] < time.time():
            raise ValueError("expired")
        return payload
    except Exception as e:
        raise HTTPException(401, f"invalid token: {e}")

def require_auth(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "no token")
    payload = verify_jwt(authorization.split(" ", 1)[1])
    return payload["sub"]

class KBEntryIn(BaseModel):
    specialty: str
    intent: str
    audience: str = "оператор"
    tone: str = "дружелюбный, профессиональный"
    do: Optional[List[str]] = None
    dont: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    text: str
    status: Literal["draft","published"] = "draft"
    tags: Optional[List[str]] = None

router = APIRouter()

def _load():
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(KB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@router.get("/kb/list")
def kb_list(status: Optional[str] = None, sub: str = Depends(require_auth)):
    items = _load()
    if status:
        items = [x for x in items if x.get("status")==status]
    return {"items": items}

@router.post("/kb/create")
def kb_create(entry: KBEntryIn, sub: str = Depends(require_auth)):
    items = _load()
    new_id = (max([x["id"] for x in items]) + 1) if items else 1
    obj = entry.dict()
    obj["id"] = new_id
    obj["created_at"] = int(time.time())
    obj["updated_at"] = int(time.time())
    items.append(obj)
    _save(items)
    return {"id": new_id}

@router.post("/kb/publish/{entry_id}")
def kb_publish(entry_id: int, sub: str = Depends(require_auth)):
    items = _load()
    found = False
    for x in items:
        if x["id"] == entry_id:
            x["status"] = "published"
            x["updated_at"] = int(time.time())
            found = True
            break
    if not found:
        raise HTTPException(404, "not found")
    _save(items)
    return {"ok": True}
