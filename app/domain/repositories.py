from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities import TodoItem


class IToDoRepository(ABC):

    @abstractmethod
    def get_all(self) -> List[TodoItem]:
        """Вернуть все задачи."""

    @abstractmethod
    def get_by_id(self, item_id: int) -> Optional[TodoItem]:
        """Найти задачу по идентификатору."""

    @abstractmethod
    def add(self, item: TodoItem) -> TodoItem:
        """Сохранить новую задачу, вернуть её с присвоенным id."""

    @abstractmethod
    def update(self, item: TodoItem) -> None:
        """Обновить существующую задачу."""

    @abstractmethod
    def delete(self, item_id: int) -> None:
        """Удалить задачу по id."""

    @abstractmethod
    def clear_completed(self) -> int:
        """Удалить все выполненные задачи, вернуть количество удалённых."""