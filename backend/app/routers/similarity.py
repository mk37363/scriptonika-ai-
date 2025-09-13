from fastapi import APIRouter
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util

router = APIRouter()

# Загружаем модель один раз при импорте
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

class Pair(BaseModel):
    text1: str
    text2: str

@router.post("/similarity")
def similarity(pair: Pair):
    e1 = model.encode(pair.text1, convert_to_tensor=True)
    e2 = model.encode(pair.text2, convert_to_tensor=True)
    cos = float(util.cos_sim(e1, e2).item())
    return {"cosine": cos}
