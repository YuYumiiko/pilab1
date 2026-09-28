"""Тесты репозитория на реальном SQLAlchemy + SQLite (in-memory)."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Явная регистрация ORM-модели в Base.metadata.
# Без этого Base.metadata.create_all() создаст пустую БД.
from app.data import models  # noqa: F401
from app.data import repository as repo_module
from app.data.database import Base
from app.data.repository import SqlAlchemyTodoRepository
from app.domain.entities import Priority, TodoItem


# =============================================================
# Fixtures
# =============================================================

@pytest.fixture
def test_session_local():
    """
    Изолированная in-memory SQLite.

    StaticPool — чтобы все сессии разделяли одно соединение,
    иначе каждая новая сессия получит пустую БД.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    # Проверяем, что модель зарегистрирована — иначе тесты молча
    # создадут пустую БД и потом будут падать на «no such table».
    assert "todo_items" in Base.metadata.tables, (
        "Модель TodoItemModel не зарегистрирована в Base.metadata. "
        "Проверьте импорт `from app.data import models`."
    )

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )

    yield session_factory

    engine.dispose()


@pytest.fixture
def repository(test_session_local, monkeypatch):
    """
    Подменяем SessionLocal в модуле repository на тестовый.

    Благодаря этому реальный SqlAlchemyTodoRepository работает
    с in-memory БД, а не с боевой todo.sqlite3.
    """
    monkeypatch.setattr(repo_module, "SessionLocal", test_session_local)
    return SqlAlchemyTodoRepository()


# =============================================================
# CRUD: добавление
# =============================================================

class TestAdd:

    def test_add_assigns_id(self, repository):
        item = TodoItem(title="Задача")
        saved = repository.add(item)
        assert saved.id is not None
        assert saved.id == 1

    def test_add_multiple(self, repository):
        a = repository.add(TodoItem(title="A"))
        b = repository.add(TodoItem(title="B"))
        assert a.id == 1
        assert b.id == 2

    def test_add_persists_all_fields(self, repository):
        deadline = datetime.now() + timedelta(days=3)
        item = TodoItem(
            title="Задача",
            priority=Priority.HIGH,
            deadline=deadline,
        )
        repository.add(item)

        loaded = repository.get_by_id(item.id)
        assert loaded is not None
        assert loaded.title == "Задача"
        assert loaded.priority == Priority.HIGH
        assert loaded.deadline == deadline
        assert loaded.is_completed is False


# =============================================================
# CRUD: чтение
# =============================================================

class TestGet:

    def test_get_all_empty(self, repository):
        assert repository.get_all() == []

    def test_get_all(self, repository):
        repository.add(TodoItem(title="A"))
        repository.add(TodoItem(title="B"))
        assert len(repository.get_all()) == 2

    def test_get_by_id(self, repository):
        saved = repository.add(TodoItem(title="A"))
        loaded = repository.get_by_id(saved.id)
        assert loaded is not None
        assert loaded.title == "A"

    def test_get_by_id_not_found(self, repository):
        assert repository.get_by_id(999) is None


# =============================================================
# CRUD: обновление
# =============================================================

class TestUpdate:

    def test_update_title(self, repository):
        item = repository.add(TodoItem(title="Старое"))
        item.change_name("Новое")
        repository.update(item)

        loaded = repository.get_by_id(item.id)
        assert loaded.title == "Новое"

    def test_update_status(self, repository):
        item = repository.add(TodoItem(title="Задача"))
        item.mark_as_completed()
        repository.update(item)
        assert repository.get_by_id(item.id).is_completed is True

    def test_update_deadline(self, repository):
        item = repository.add(TodoItem(title="Задача"))
        future = datetime.now() + timedelta(days=7)
        item.change_deadline(future)
        repository.update(item)
        assert repository.get_by_id(item.id).deadline == future

    def test_update_non_existing_raises(self, repository):
        ghost = TodoItem(title="Ghost", item_id=999)
        with pytest.raises(ValueError, match="не найдена"):
            repository.update(ghost)

    def test_update_without_id_raises(self, repository):
        ghost = TodoItem(title="Ghost")
        with pytest.raises(ValueError, match="без id"):
            repository.update(ghost)


# =============================================================
# CRUD: удаление
# =============================================================

class TestDelete:

    def test_delete(self, repository):
        item = repository.add(TodoItem(title="A"))
        repository.delete(item.id)
        assert repository.get_by_id(item.id) is None

    def test_delete_non_existing_is_noop(self, repository):
        repository.delete(999)  # не должно бросать


class TestClearCompleted:

    def test_clear_completed(self, repository):
        repository.add(TodoItem(title="A"))
        repository.add(TodoItem(title="B", is_completed=True))
        repository.add(TodoItem(title="C", is_completed=True))

        removed = repository.clear_completed()
        assert removed == 2
        remaining = repository.get_all()
        assert [t.title for t in remaining] == ["A"]

    def test_clear_completed_when_none(self, repository):
        repository.add(TodoItem(title="A"))
        assert repository.clear_completed() == 0
        assert len(repository.get_all()) == 1


# =============================================================
# Маппинг domain ↔ ORM
# =============================================================

class TestMapping:

    def test_priority_roundtrip(self, repository):
        for p in (Priority.LOW, Priority.MEDIUM, Priority.HIGH):
            item = repository.add(
                TodoItem(title=f"Задача-{p.value}", priority=p)
            )
            loaded = repository.get_by_id(item.id)
            assert loaded.priority == p

    def test_deadline_none_roundtrip(self, repository):
        item = repository.add(TodoItem(title="Задача"))
        loaded = repository.get_by_id(item.id)
        assert loaded.deadline is None

    def test_created_at_persisted(self, repository):
        item = repository.add(TodoItem(title="Задача"))
        loaded = repository.get_by_id(item.id)
        # В пределах секунды — SQLite хранит с точностью до микросекунд,
        # но при сериализации может незначительно отличаться
        assert abs((loaded.created_at - item.created_at).total_seconds()) < 1

    def test_overdue_task_can_be_loaded(self, repository):

        past = datetime.now() - timedelta(days=1)

        from app.data.models import TodoItemModel
        with repo_module.SessionLocal() as session:
            session.add(TodoItemModel(
                title="Просроченная",
                is_completed=False,
                priority=Priority.MEDIUM.value,
                created_at=datetime.now() - timedelta(days=10),
                deadline=past,
            ))
            session.commit()

        loaded = repository.get_by_id(1)
        assert loaded is not None
        assert loaded.deadline == past