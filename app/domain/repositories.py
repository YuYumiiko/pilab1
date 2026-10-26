from __future__ import annotations
from abc import ABC, abstractmethod
from app.domain.entities import TodoItem


class ITodoRepository(ABC):

    @abstractmethod
    def add(self, item: TodoItem) -> TodoItem:
        ...

    @abstractmethod
    def get_all(self) -> list[TodoItem]:
        ...

    @abstractmethod
    def delete(self, item_id: int) -> None:
        ...

    @abstractmethod
    def update(self, item: TodoItem) -> None:
        ...