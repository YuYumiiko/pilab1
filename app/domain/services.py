from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from app.domain.entities import Priority, TodoItem
from app.domain.repositories import IToDoRepository


class TaskFilter(str, Enum):
    ALL = "all"
    ACTIVE = "active"
    COMPLETED = "completed"


class SortMode(str, Enum):
    BY_CREATED = "by_created"      # По дате создания (по умолчанию)
    BY_PRIORITY = "by_priority"    # По приоритету (High → Low, затем по дате)
    BY_DEADLINE = "by_deadline"    # По дедлайну (раньше — выше, без дедлайна — в конце)


# Порядок приоритетов для сортировки
_PRIORITY_ORDER = {
    Priority.HIGH: 0,
    Priority.MEDIUM: 1,
    Priority.LOW: 2,
}


class TodoService:

    def __init__(self, repository: IToDoRepository) -> None:
        self._repository = repository

    # ---------- Создание ----------

    def create_task(
        self,
        title: str,
        priority: Priority = Priority.MEDIUM,
        deadline: Optional[datetime] = None,
    ) -> TodoItem:
        """Создать новую задачу с указанным приоритетом и дедлайном."""
        item = TodoItem(
            title=title,
            priority=priority,
            deadline=deadline,
        )
        return self._repository.add(item)

    # ---------- Чтение ----------

    def get_tasks(
        self,
        task_filter: TaskFilter = TaskFilter.ALL,
        sort_mode: SortMode = SortMode.BY_CREATED,
    ) -> List[TodoItem]:

        items = self._repository.get_all()

        # Фильтр по статусу
        if task_filter == TaskFilter.ACTIVE:
            items = [i for i in items if not i.is_completed]
        elif task_filter == TaskFilter.COMPLETED:
            items = [i for i in items if i.is_completed]

        return self._sort(items, sort_mode)

    def get_statistics(self) -> dict:
        items = self._repository.get_all()
        completed = sum(1 for i in items if i.is_completed)
        return {
            "total": len(items),
            "completed": completed,
            "active": len(items) - completed,
        }

    # ---------- Изменение ----------

    def toggle_completion(self, item_id: int) -> None:
        item = self._repository.get_by_id(item_id)
        if item is None:
            raise ValueError(f"Задача с id={item_id} не найдена")
        item.toggle_completion()
        self._repository.update(item)

    def update_task(
        self,
        item_id: int,
        title: str,
        priority: Priority,
        deadline: Optional[datetime],
    ) -> None:

        item = self._repository.get_by_id(item_id)
        if item is None:
            raise ValueError(f"Задача с id={item_id} не найдена")

        if title != item.title:
            item.change_name(title)
        if priority != item.priority:
            item.change_priority(priority)
        if deadline != item.deadline:
            item.change_deadline(deadline)

        self._repository.update(item)

    # ---------- Удаление ----------

    def delete_task(self, item_id: int) -> None:
        """Удалить задачу по идентификатору."""
        self._repository.delete(item_id)

    def clear_completed(self) -> int:
        """Удалить все выполненные задачи. Вернуть количество удалённых."""
        return self._repository.clear_completed()

    # ---------- Приватные хелперы ----------

    @staticmethod
    def _sort(items: List[TodoItem], sort_mode: SortMode) -> List[TodoItem]:
        """Отсортировать список задач согласно выбранному режиму."""
        if sort_mode == SortMode.BY_PRIORITY:
            return sorted(
                items,
                key=lambda i: (_PRIORITY_ORDER[i.priority], i.created_at),
            )
        if sort_mode == SortMode.BY_DEADLINE:
            # Задачи с дедлайном — по возрастанию; без дедлайна — в конце
            return sorted(
                items,
                key=lambda i: (
                    i.deadline is None,
                    i.deadline or datetime.max,
                    i.created_at,
                ),
            )
        # По умолчанию — по дате создания
        return sorted(items, key=lambda i: i.created_at)