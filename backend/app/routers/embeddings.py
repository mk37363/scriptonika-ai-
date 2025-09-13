# backend/app/routers/embeddings.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np

from sentence_transformers import SentenceTransformer
from .similarity import model  # используем ту же модель
from ..vectorstore import get_or_create

router = APIRouter()

class EmbedIn(BaseModel):
    text: str

class EmbedOut(BaseModel):
    vector: List[float]

class AddIn(BaseModel):
    texts: List[str]

class SearchIn(BaseModel):
    query: str
    top_k: int = 5

@router.get("/health")
def health():
    try:
        _ = model.get_sentence_embedding_dimension()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/embed", response_model=EmbedOut)
def embed(payload: EmbedIn):
    vec = model.encode(payload.text, convert_to_tensor=False)  # numpy 1D
    return {"vector": [float(x) for x in vec]}

@router.post("/index/{name}/add")
def index_add(name: str, payload: AddIn):
    if not payload.texts:
        raise HTTPException(400, "texts is empty")
    embs = model.encode(payload.texts, convert_to_tensor=False)  # (n, d) numpy
    store = get_or_create(name, dim=len(embs[0]))
    ids = store.add(np.array(embs), payload.texts)
    return {"count": len(ids), "ids": ids}

@router.post("/index/{name}/search")
def index_search(name: str, payload: SearchIn):
    store = get_or_create(name, dim=model.get_sentence_embedding_dimension())
    if store.index.ntotal == 0:
        return {"hits": []}
    q = model.encode([payload.query], convert_to_tensor=False)  # (1, d)
    ids, scores = store.search(np.array(q), k=payload.top_k)
    hits = [{"id": i, "score": float(s), "text": store.texts[i]} for i, s in zip(ids, scores) if i != -1]
    return {"hits": hits}
