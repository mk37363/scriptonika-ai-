# -*- coding: utf-8 -*-
"""
Общий модуль БД: движок, базовый класс ORM и зависимость get_db()
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

DB_DIR = "/opt/skriptonika/ops/data"
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "app.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False — чтобы работать из разных потоков (uvicorn workers)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость FastAPI: отдаёт сессию и корректно закрывает её.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
