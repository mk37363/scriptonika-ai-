# -*- coding: utf-8 -*-
"""
Skriptonika AI API — main.py
- Интеграция с GigaChat (freemium: GigaChat:preview)
- Проекты / Чаты / Сообщения (история диалогов)
"""
from __future__ import annotations

import os
import time
import uuid
from typing import Optional

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# .env (опционально)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv("/opt/skriptonika/ops/.env")
except Exception:
    pass

# ==== GigaChat config ====
GIGACHAT_BASE_URL = os.getenv("GIGACHAT_BASE_URL", "https://gigachat.devices.sberbank.ru/api/v1")
GIGACHAT_NGW_URL = os.getenv("GIGACHAT_NGW_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
GIGACHAT_AUTH_BASIC = os.getenv("GIGACHAT_AUTH_BASIC")
if not GIGACHAT_AUTH_BASIC:
    raise RuntimeError("GIGACHAT_AUTH_BASIC не найден — проверь окружение")

_gc_token: Optional[str] = None
_gc_token_exp: float = 0.0


def _need_new_token() -> bool:
    return (not _gc_token) or (time.time() >= _gc_token_exp - 5 * 60)


def _get_gigachat_token() -> str:
    global _gc_token, _gc_token_exp
    if not _need_new_token():
        return _gc_token  # type: ignore

    try:
        r = requests.post(
            GIGACHAT_NGW_URL,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": str(uuid.uuid4()),
                "Authorization": f"Basic {GIGACHAT_AUTH_BASIC}",
            },
            data={"scope": GIGACHAT_SCOPE},
            timeout=20,
            verify=False,
        )
        r.raise_for_status()
        data = r.json()
        token = data.get("access_token")
        expires_in = int(data.get("expires_in", 1800))
        if not token:
            raise RuntimeError("NGW: нет access_token")
        _gc_token = token
        _gc_token_exp = time.time() + max(60, expires_in)
        return _gc_token
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OAuth NGW error: {e}")


def ask_gigachat(prompt: str) -> str:
    token = _get_gigachat_token()
    try:
        r = requests.post(
            f"{GIGACHAT_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "model": "GigaChat:preview",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=40,
            verify=False,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"GigaChat error: {e}")


# ==== FastAPI ====
app = FastAPI(title="Skriptonika AI API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем ORM и создаём таблицы
from .db import Base, engine  # noqa: E402
from .routers import projects as projects_router  # noqa: E402
from .routers import chats as chats_router       # noqa: E402
from .routers import messages as messages_router # noqa: E402
from .schemas import ChatOut, MessageOut         # noqa: F401 (может пригодиться в документации)


@app.on_event("startup")
def on_startup():
    # создаём таблицы при старте, если их ещё нет
    Base.metadata.create_all(bind=engine)
    # мягкий разогрев токена
    try:
        _ = _get_gigachat_token()
    except Exception:
        pass


# Health
@app.get("/", tags=["health"])
def root():
    return {"status": "ok"}

@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}


# Прямой чат (как было)
from pydantic import BaseModel  # noqa: E402

class ChatIn(BaseModel):
    message: str

class ChatReply(BaseModel):
    reply: str

@app.post("/api/chat", response_model=ChatReply, tags=["ai"])
def chat(in_: ChatIn):
    return {"reply": ask_gigachat(in_.message)}

@app.post("/api/ask", response_model=ChatReply, tags=["ai"])
def ask(in_: ChatIn):
    # здесь позже подключим RAG; пока — прямой вызов
    return {"reply": ask_gigachat(in_.message)}


# Подключаем новые CRUD-роуты
app.include_router(projects_router.router)
app.include_router(chats_router.router)
app.include_router(messages_router.router)
