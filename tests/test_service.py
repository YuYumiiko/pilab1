from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pytest

from app.domain.entities import Priority, TodoItem
from app.domain.repositories import IToDoRepository
from app.domain.services import SortMode, TaskFilter, TodoService


class FakeRepository(IToDoRepository):

    def __init__(self) -> None:
        self._items: Dict[int, TodoItem] = {}
        self._next_id = 1

    def get_all(self) -> List[TodoItem]:
        return list(self._items.values())

    def get_by_id(self, item_id: int) -> Optional[TodoItem]:
        return self._items.get(item_id)

    def add(self, item: TodoItem) -> TodoItem:
        item.assign_id(self._next_id)
        self._items[self._next_id] = item
        self._next_id += 1
        return item

    def update(self, item: TodoItem) -> None:
        if item.id is None or item.id not in self._items:
            raise ValueError(f"Задача id={item.id} не найдена")
        self._items[item.id] = item

    def delete(self, item_id: int) -> None:
        self._items.pop(item_id, None)

    def clear_completed(self) -> int:
        to_delete = [i for i in self._items if self._items[i].is_completed]
        for i in to_delete:
            del self._items[i]
        return len(to_delete)


@pytest.fixture
def repository() -> FakeRepository:
    return FakeRepository()


@pytest.fixture
def service(repository: FakeRepository) -> TodoService:
    return TodoService(repository)

# ---------- Создание ----------

class TestCreateTask:

    def test_create_simple_task(self, service):
        item = service.create_task("Купить хлеб")
        assert item.id == 1
        assert item.title == "Купить хлеб"
        assert item.priority == Priority.MEDIUM
        assert item.deadline is None

    def test_create_task_with_priority_and_deadline(self, service):
        deadline = datetime.now() + timedelta(days=3)
        item = service.create_task(
            "Сдать лабу",
            priority=Priority.HIGH,
            deadline=deadline,
        )
        assert item.priority == Priority.HIGH
        assert item.deadline == deadline

    def test_create_task_with_empty_title_raises(self, service):
        with pytest.raises(ValueError, match="не может быть пустым"):
            service.create_task("   ")

    def test_create_task_with_past_deadline_raises(self, service):
        past = datetime.now() - timedelta(days=1)
        with pytest.raises(ValueError, match="не может быть в прошлом"):
            service.create_task("Задача", deadline=past)


# ---------- Чтение и фильтрация ----------

class TestGetTasks:

    def test_empty_repository(self, service):
        assert service.get_tasks() == []

    def test_get_all(self, service):
        service.create_task("A")
        service.create_task("B")
        tasks = service.get_tasks(TaskFilter.ALL)
        assert len(tasks) == 2

    def test_filter_active(self, service):
        service.create_task("A")
        b = service.create_task("B")
        service.toggle_completion(b.id)
        tasks = service.get_tasks(TaskFilter.ACTIVE)
        assert [t.title for t in tasks] == ["A"]

    def test_filter_completed(self, service):
        service.create_task("A")
        b = service.create_task("B")
        service.toggle_completion(b.id)
        tasks = service.get_tasks(TaskFilter.COMPLETED)
        assert [t.title for t in tasks] == ["B"]


# ---------- Сортировка ----------

class TestSorting:

    def test_sort_by_created_default(self, service):
        a = service.create_task("A")
        b = service.create_task("B")
        c = service.create_task("C")
        tasks = service.get_tasks(sort_mode=SortMode.BY_CREATED)
        assert [t.title for t in tasks] == ["A", "B", "C"]

    def test_sort_by_priority(self, service):
        service.create_task("Low", priority=Priority.LOW)
        service.create_task("High", priority=Priority.HIGH)
        service.create_task("Medium", priority=Priority.MEDIUM)
        tasks = service.get_tasks(sort_mode=SortMode.BY_PRIORITY)
        assert [t.title for t in tasks] == ["High", "Medium", "Low"]

    def test_sort_by_deadline_puts_none_last(self, service):
        service.create_task("NoDeadline")
        service.create_task(
            "Later",
            deadline=datetime.now() + timedelta(days=5),
        )
        service.create_task(
            "Sooner",
            deadline=datetime.now() + timedelta(days=1),
        )
        tasks = service.get_tasks(sort_mode=SortMode.BY_DEADLINE)
        assert [t.title for t in tasks] == ["Sooner", "Later", "NoDeadline"]

# ---------- Переключение статуса ----------

class TestToggleCompletion:

    def test_toggle_existing_task(self, service):
        item = service.create_task("Задача")
        service.toggle_completion(item.id)
        assert service.get_tasks()[0].is_completed is True

    def test_toggle_twice_returns_to_active(self, service):
        item = service.create_task("Задача")
        service.toggle_completion(item.id)
        service.toggle_completion(item.id)
        assert service.get_tasks()[0].is_completed is False

    def test_toggle_non_existing_raises(self, service):
        with pytest.raises(ValueError, match="не найдена"):
            service.toggle_completion(999)

# ---------- Обновление ----------

class TestUpdateTask:

    def test_update_title(self, service):
        item = service.create_task("Старое")
        service.update_task(item.id, "Новое", Priority.MEDIUM, None)
        assert service.get_tasks()[0].title == "Новое"

    def test_update_priority(self, service):
        item = service.create_task("Задача")
        service.update_task(item.id, "Задача", Priority.HIGH, None)
        assert service.get_tasks()[0].priority == Priority.HIGH

    def test_update_deadline(self, service):
        item = service.create_task("Задача")
        future = datetime.now() + timedelta(days=7)
        service.update_task(item.id, "Задача", Priority.MEDIUM, future)
        assert service.get_tasks()[0].deadline == future

    def test_update_deadline_to_none(self, service):
        future = datetime.now() + timedelta(days=1)
        item = service.create_task("Задача", deadline=future)
        service.update_task(item.id, "Задача", Priority.MEDIUM, None)
        assert service.get_tasks()[0].deadline is None

    def test_update_non_existing_raises(self, service):
        with pytest.raises(ValueError, match="не найдена"):
            service.update_task(999, "X", Priority.HIGH, None)

    def test_update_overdue_task_without_touching_deadline(self, service):
        """Нельзя «сбросить» дедлайн, если мы его не трогали."""
        past = datetime.now() - timedelta(days=1)
        # Обойдём валидацию, создав просроченную задачу через домен
        item = TodoItem(title="Старая", item_id=1, deadline=past)
        service._repository._items[1] = item
        service._repository._next_id = 2

        # Меняем только название — дедлайн должен сохраниться
        service.update_task(item.id, "Новая", Priority.MEDIUM, past)
        assert service.get_tasks()[0].deadline == past

# ---------- Удаление ----------

class TestDelete:

    def test_delete_existing(self, service):
        item = service.create_task("Задача")
        service.delete_task(item.id)
        assert service.get_tasks() == []

    def test_delete_non_existing_is_noop(self, service):
        service.delete_task(999)  # не должно бросать
        assert service.get_tasks() == []

    def test_clear_completed(self, service):
        service.create_task("A")
        b = service.create_task("B")
        service.create_task("C")
        service.toggle_completion(b.id)
        removed = service.clear_completed()
        assert removed == 1
        assert [t.title for t in service.get_tasks()] == ["A", "C"]

    def test_clear_completed_when_none_returns_zero(self, service):
        service.create_task("A")
        assert service.clear_completed() == 0

# ---------- Статистика ----------

class TestStatistics:

    def test_empty(self, service):
        stats = service.get_statistics()
        assert stats == {"total": 0, "completed": 0, "active": 0}

    def test_mixed(self, service):
        service.create_task("A")
        b = service.create_task("B")
        service.create_task("C")
        service.toggle_completion(b.id)
        stats = service.get_statistics()
        assert stats == {"total": 3, "completed": 1, "active": 2}