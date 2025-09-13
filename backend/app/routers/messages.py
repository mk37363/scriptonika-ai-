# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Chat, Message
from ..schemas import MessageCreate, MessageOut
from ..main import ask_gigachat  # используем твой уже готовый вызов

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("", response_model=MessageOut)
def send_message(data: MessageCreate, db: Session = Depends(get_db)):
    chat = db.get(Chat, data.chat_id)
    if not chat:
        raise HTTPException(404, detail="Чат не найден")

    # 1) сохраняем юзерское сообщение
    m_user = Message(chat_id=data.chat_id, role="user", content=data.message)
    db.add(m_user)
    db.commit()
    db.refresh(m_user)

    # 2) получаем ответ GigaChat
    reply_text = ask_gigachat(data.message)

    # 3) сохраняем ответ ассистента
    m_bot = Message(chat_id=data.chat_id, role="assistant", content=reply_text)
    db.add(m_bot)
    db.commit()
    db.refresh(m_bot)

    # возвращаем последнее сообщение ассистента (удобно для фронта)
    return m_bot
