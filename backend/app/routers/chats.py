# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Project, Chat, Message
from ..schemas import ChatCreate, ChatOut, ChatWithMessages, MessageOut

router = APIRouter(prefix="/api/chats", tags=["chats"])


@router.post("", response_model=ChatOut, status_code=201)
def create_chat(data: ChatCreate, db: Session = Depends(get_db)):
    project = db.get(Project, data.project_id)
    if not project:
        raise HTTPException(404, detail="Проект не найден")
    chat = Chat(project_id=data.project_id, title=data.title or "Новый чат")
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


@router.get("/{chat_id}", response_model=ChatWithMessages)
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(404, detail="Чат не найден")
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.id.asc()).all()
    return ChatWithMessages(chat=chat, messages=messages)
