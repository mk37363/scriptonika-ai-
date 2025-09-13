# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Project, Chat
from ..schemas import ProjectCreate, ProjectOut, ChatOut

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.id.asc()).all()


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    exists = db.query(Project).filter(Project.name == data.name).first()
    if exists:
        raise HTTPException(409, detail="Проект с таким именем уже существует")
    obj = Project(name=data.name, description=data.description)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{project_id}/chats", response_model=List[ChatOut])
def list_project_chats(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, detail="Проект не найден")
    return db.query(Chat).filter(Chat.project_id == project_id).order_by(Chat.id.asc()).all()
