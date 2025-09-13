# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class _Model(BaseModel):
    model_config = dict(from_attributes=True)  # Pydantic v2: ORM-mode


# -------- Projects
class ProjectCreate(_Model):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None


class ProjectOut(_Model):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime


# -------- Chats
class ChatCreate(_Model):
    project_id: int
    title: Optional[str] = "Новый чат"


class ChatOut(_Model):
    id: int
    project_id: int
    title: str
    created_at: datetime


# -------- Messages
class MessageCreate(_Model):
    chat_id: int
    message: str


class MessageOut(_Model):
    id: int
    chat_id: int
    role: str
    content: str
    created_at: datetime


class ChatWithMessages(_Model):
    chat: ChatOut
    messages: List[MessageOut]
