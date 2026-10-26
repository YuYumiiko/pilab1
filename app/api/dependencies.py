from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.domain.repositories import ITodoRepository
from app.domain.services import TodoService
from app.infrastructure.database import create_session_factory
from app.infrastructure.repository import SqlAlchemyTodoRepo

_session_factory = create_session_factory("todo.sqlite3")

def get_session() -> Generator[Session, None, None]:
    with _session_factory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

def get_repository(session: Session = Depends(get_session)) -> ITodoRepository:
    return SqlAlchemyTodoRepo(session)

def get_service(repository: ITodoRepository = Depends(get_repository)) -> TodoService:
    return TodoService(repository)