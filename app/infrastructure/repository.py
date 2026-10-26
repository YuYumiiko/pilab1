from __future__ import annotations

from sentry_sdk.session import Session
from sqlalchemy import select
from sqlalchemy.orm import  sessionmaker

from app.infrastructure.models import TodoModel
from app.domain.entities import TodoItem
from app.domain.repositories import ITodoRepository


class SqlAlchemyTodoRepo(ITodoRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, item: TodoItem) -> TodoItem:
        model = self._to_model(item)
        self._session.add(model)
        self._session.flush()
        item.assign_id(model.id)
        return item

    def get_all(self) -> list[TodoItem]:
        stmt = select(TodoModel).order_by(TodoModel.created_at)
        models = self._session.scalars(stmt).all()
        return [self._to_domain(m) for m in models]

    def delete(self, item_id: int) -> None:
        model = self._session.get(TodoModel, item_id)
        if model is not None:
            self._session.delete(model)
            self._session.flush()

    def update(self, item: TodoItem) -> None:
        if item.id is None:
            raise ValueError("Нельзя обновить задачу без ID")
        model = self._session.get(TodoModel, item.id)
        if model is None:
            raise ValueError("Задача с таким ID не найдена в БД")
        model.title = item.title
        model.priority = item.priority
        model.is_completed = item.is_completed
        model.created_at = item.created_at
        model.deadline = item.deadline
        self._session.flush()

    @staticmethod
    def _to_model(item: TodoItem) -> TodoModel:
        model = TodoModel()
        model.title = item.title
        model.is_completed = item.is_completed
        model.priority = item.priority
        model.created_at = item.created_at
        model.deadline = item.deadline
        return model

    @staticmethod
    def _to_domain(model: TodoModel) -> TodoItem:
        return TodoItem(
            title=model.title,
            priority=model.priority,
            item_id=model.id,
            is_completed=model.is_completed,
            created_at=model.created_at,
            deadline=model.deadline,
        )