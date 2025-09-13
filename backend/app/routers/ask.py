from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os, numpy as np

from .similarity import model as st_model
from ..vectorstore import get_or_create

# Опциональный импорт провайдера
USE_GIGACHAT = bool(os.getenv("GIGACHAT_CLIENT_ID") and os.getenv("GIGACHAT_CLIENT_SECRET"))
if USE_GIGACHAT:
    from ..llm.gigachat import ask_gigachat

router = APIRouter()

class AskIn(BaseModel):
    index: str = "default"
    question: str
    top_k: int = 5

class AskOut(BaseModel):
    answer: str
    contexts: List[str]

SYSTEM = (
"Ты ассистент Скриптоники. Отвечай кратко, профессионально и дружелюбно. "
"Используй только факты из КОНТЕКСТА. Если ответа нет в контексте — скажи, какие данные нужны."
)

def build_prompt(question: str, contexts: List[str]) -> str:
    blocks = "\n\n---\n\n".join(contexts)
    return f"{SYSTEM}\n\nКОНТЕКСТ:\n{blocks}\n\nВОПРОС:\n{question}\n\nОТВЕТ:"

@router.post("/ask", response_model=AskOut)
def ask(payload: AskIn):
    store = get_or_create(payload.index, dim=st_model.get_sentence_embedding_dimension())
    if store.index.ntotal == 0:
        raise HTTPException(400, "Индекс пуст. Сначала добавьте тексты через /api/index/{name}/add")

    q = st_model.encode([payload.question], convert_to_numpy=True)
    ids, scores = store.search(np.array(q), k=payload.top_k)
    ctx = [store.texts[i] for i in ids if i != -1][:payload.top_k]

    # Попытка спросить у GigaChat, если ключи заданы
    if USE_GIGACHAT:
        try:
            prompt = build_prompt(payload.question, ctx)
            answer = ask_gigachat(prompt)
            return AskOut(answer=answer, contexts=ctx)
        except Exception as e:
            # упасть в фоллбэк, чтобы API не 502
            pass

    # Фоллбэк-ответ без LLM
    answer = "Найденные фрагменты:\n\n" + "\n---\n".join(ctx)
    return AskOut(answer=answer, contexts=ctx)
