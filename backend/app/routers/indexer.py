from fastapi import APIRouter, HTTPException, Header, Depends
import os, json, time, numpy as np
from sentence_transformers import SentenceTransformer
from .kb_admin import verify_jwt
from ..vectorstore import get_or_create

router = APIRouter()

INDEX_NAME = "default"
KB_PATH = "/opt/skriptonika/kb/kb.json"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def require_auth(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "no token")
    payload = verify_jwt(authorization.split(" ", 1)[1])
    return payload["sub"]

def _flatten(entry):
    blocks = [entry.get("text","")]
    for key in ("do","dont","examples"):
        arr = entry.get(key)
        if arr:
            blocks.extend(arr if isinstance(arr, list) else [str(arr)])
    # Немного метаданных для качества выдачи
    meta = f"[{entry.get('specialty','')}] [{entry.get('intent','')}] тон: {entry.get('tone','')}"
    blocks.append(meta)
    return "\n".join([b for b in blocks if b]).strip()

@router.post("/reindex")
def reindex(sub: str = Depends(require_auth)):
    if not os.path.exists(KB_PATH):
        raise HTTPException(400, "KB is empty")
    with open(KB_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)
    pub = [x for x in items if x.get("status") == "published"]
    if not pub:
        raise HTTPException(400, "Нет опубликованных записей")

    texts = [_flatten(x) for x in pub]
    embs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).astype("float32")

    store = get_or_create(INDEX_NAME, dim=model.get_sentence_embedding_dimension())
    store.index.reset()
    store.texts = []
    store.add(np.array(embs), texts)
    return {"ok": True, "count": len(texts)}
