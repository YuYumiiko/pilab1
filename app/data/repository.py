from __future__ import annotations

from typing import List, Optional

from app.data.database import SessionLocal
from app.data.models import TodoItemModel
from app.domain.entities import Priority, TodoItem
from app.domain.repositories import IToDoRepository


class SqlAlchemyTodoRepository(IToDoRepository):

    # ---------- Публичные методы IToDoRepository ----------

    def get_all(self) -> List[TodoItem]:
        with SessionLocal() as session:
            rows = session.query(TodoItemModel).all()
            return [self._to_domain(r) for r in rows]

    def get_by_id(self, item_id: int) -> Optional[TodoItem]:
        with SessionLocal() as session:
            row = session.get(TodoItemModel, item_id)
            return self._to_domain(row) if row else None

    def add(self, item: TodoItem) -> TodoItem:
        with SessionLocal() as session:
            row = TodoItemModel(
                title=item.title,
                is_completed=item.is_completed,
                priority=item.priority.value,
                created_at=item.created_at,
                deadline=item.deadline,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            item.assign_id(row.id)
            return item

    def update(self, item: TodoItem) -> None:
        if item.id is None:
            raise ValueError("Нельзя обновить задачу без id")
        with SessionLocal() as session:
            row = session.get(TodoItemModel, item.id)
            if row is None:
                raise ValueError(f"Задача id={item.id} не найдена в БД")
            row.title = item.title
            row.is_completed = item.is_completed
            row.priority = item.priority.value
            row.deadline = item.deadline
            session.commit()

    def delete(self, item_id: int) -> None:
        with SessionLocal() as session:
            row = session.get(TodoItemModel, item_id)
            if row is not None:
                session.delete(row)
                session.commit()

    def clear_completed(self) -> int:
        with SessionLocal() as session:
            deleted = (
                session.query(TodoItemModel)
                .filter(TodoItemModel.is_completed.is_(True))
                .delete(synchronize_session=False)
            )
            session.commit()
            return int(deleted)

    # ---------- Приватные методы маппинга ----------

    @staticmethod
    def _to_domain(row: TodoItemModel) -> TodoItem:

        try:
            priority = Priority(row.priority)
        except ValueError:
            priority = Priority.MEDIUM
        return TodoItem(
            item_id=row.id,
            title=row.title,
            is_completed=row.is_completed,
            priority=priority,
            created_at=row.created_at,
            deadline=row.deadline,
        )