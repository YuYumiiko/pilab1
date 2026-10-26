from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from datetime import datetime

MAX_TITLE_LENGTH = 500

class Priority(Enum):
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"


class TodoItem:
    def __init__(
        self,
        title: str,
        priority: Priority = Priority.MEDIUM,
        item_id: int | None = None,
        is_completed: bool = False,
        created_at: datetime | None = None,
        deadline: datetime | None = None,
    ) -> None:
        self._id = item_id
        self._title = ""
        self._priority = priority
        self._is_completed = is_completed
        self._created_at = created_at or datetime.now()
        self._deadline = deadline

        self.change_title(title)

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def priority(self) -> Priority:
        return self._priority

    @property
    def is_completed(self) -> bool:
        return self._is_completed

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def deadline(self) -> datetime | None:
        return self._deadline

    def change_title(self, new_title: str) -> None:
        if new_title is None or not new_title.strip():
            raise ValueError("Нельзя оставить задачу без названия!")
        cleand = new_title.strip()
        if len(new_title) > MAX_TITLE_LENGTH:
            raise ValueError(f"Превышено максимальное число символов {MAX_TITLE_LENGTH}")
        self._title = cleand

    def change_priority(self, new_priority: Priority) -> None:
        if not isinstance(new_priority, Priority):
            raise TypeError("Приоритет не соответсвует существующим!")
        self._priority = new_priority

    def change_deadline(self, new_deadline: datetime | None) -> None:
        if new_deadline is not None and new_deadline < self._created_at:
            raise ValueError(
                "Дедлайн не может быть раньше даты создания задачи"
            )
        self._deadline = new_deadline

    def assign_id(self, new_id) -> None:
        if self._id is not None:
            raise ValueError("ID уже присвоен")
        self._id = new_id

    def toggle_completed(self) -> None:
        self._is_completed = not self._is_completed

    def mark_as_completed(self) -> None:
        self._is_completed = True

    def mark_as_active(self) -> None:
        self._is_completed = False


    def __repr__(self) -> str:
        status = "+" if self._is_completed else "0"
        dl = self._deadline.strftime("%d.%m.%Y %H:%M") if self._deadline else "—"
        return (
            f"<TodoItem id={self._id} {status} '{self._title}' "
            f"[{self._priority.value}] deadline={dl}>"
        )