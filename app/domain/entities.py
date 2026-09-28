from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional


class Priority(str, Enum):
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"


class TodoItem:

    def __init__(
        self,
        title: str,
        item_id: Optional[int] = None,
        is_completed: bool = False,
        priority: Priority = Priority.MEDIUM,
        created_at: Optional[datetime] = None,
        deadline: Optional[datetime] = None,
    ) -> None:
        self._validate_title(title)
        self._id = item_id
        self._title = title.strip()
        self._is_completed = is_completed
        self._priority = priority
        self._created_at = created_at or datetime.now()
        if deadline is not None:
            self._validate_deadline(deadline, check_past=(item_id is None))
        self._deadline = deadline


    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def is_completed(self) -> bool:
        return self._is_completed

    @property
    def priority(self) -> Priority:
        return self._priority

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def deadline(self) -> Optional[datetime]:
        return self._deadline


    def mark_as_completed(self) -> None:
        self._is_completed = True

    def mark_as_active(self) -> None:
        self._is_completed = False

    def toggle_completion(self) -> None:
        self._is_completed = not self._is_completed

    def change_name(self, new_title: str) -> None:
        self._validate_title(new_title)
        self._title = new_title.strip()

    def change_priority(self, new_priority: Priority) -> None:
        if not isinstance(new_priority, Priority):
            raise ValueError("Приоритет должен быть значением Priority")
        self._priority = new_priority

    def change_deadline(self, new_deadline: Optional[datetime]) -> None:
        if new_deadline is not None:
            self._validate_deadline(new_deadline, check_past=True)
        self._deadline = new_deadline


    def assign_id(self, item_id: int) -> None:
        if self._id is not None:
            raise ValueError("Идентификатор уже задан")
        self._id = item_id


    @staticmethod
    def _validate_title(title: str) -> None:
        if not isinstance(title, str):
            raise ValueError("Название должно быть строкой")
        if not title.strip():
            raise ValueError("Название задачи не может быть пустым")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TodoItem):
            return NotImplemented
        return self._id is not None and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        status = "✓" if self._is_completed else "·"
        return f"<TodoItem {status} #{self._id} {self._title!r}>"

    @staticmethod
    def _validate_deadline(deadline: datetime, check_past: bool = True) -> None:
        if not isinstance(deadline, datetime):
            raise ValueError("Дедлайн должен быть datetime")
        if check_past and deadline < datetime.now():
            raise ValueError("Дедлайн не может быть в прошлом")