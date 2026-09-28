from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.domain.entities import Priority, TodoItem


# ---------- Инварианты названия ----------

class TestTitleInvariants:

    def test_create_with_valid_title(self):
        item = TodoItem(title="Купить хлеб")
        assert item.title == "Купить хлеб"

    def test_title_is_stripped(self):
        item = TodoItem(title="  Позвонить маме  ")
        assert item.title == "Позвонить маме"

    def test_empty_title_raises(self):
        with pytest.raises(ValueError, match="не может быть пустым"):
            TodoItem(title="")

    def test_whitespace_only_title_raises(self):
        with pytest.raises(ValueError, match="не может быть пустым"):
            TodoItem(title="   ")

    def test_non_string_title_raises(self):
        with pytest.raises(ValueError, match="должно быть строкой"):
            TodoItem(title=123)  # type: ignore[arg-type]

    def test_change_name_to_valid(self):
        item = TodoItem(title="Старое")
        item.change_name("Новое")
        assert item.title == "Новое"

    def test_change_name_to_empty_raises(self):
        item = TodoItem(title="Старое")
        with pytest.raises(ValueError):
            item.change_name("   ")
        # Название не изменилось
        assert item.title == "Старое"


# ---------- Инварианты дедлайна ----------

class TestDeadlineInvariants:

    def test_deadline_in_future_is_ok(self):
        future = datetime.now() + timedelta(days=1)
        item = TodoItem(title="Задача", deadline=future)
        assert item.deadline == future

    def test_deadline_in_past_raises_on_create(self):
        past = datetime.now() - timedelta(days=1)
        with pytest.raises(ValueError, match="не может быть в прошлом"):
            TodoItem(title="Задача", deadline=past)

    def test_deadline_in_past_is_allowed_when_loading_from_db(self):
        """Загрузка из БД (item_id задан) не должна падать на просроченном дедлайне."""
        past = datetime.now() - timedelta(days=1)
        item = TodoItem(title="Старая", item_id=42, deadline=past)
        assert item.deadline == past

    def test_change_deadline_to_past_raises(self):
        item = TodoItem(title="Задача")
        past = datetime.now() - timedelta(days=1)
        with pytest.raises(ValueError, match="не может быть в прошлом"):
            item.change_deadline(past)

    def test_change_deadline_to_none_removes_it(self):
        future = datetime.now() + timedelta(days=1)
        item = TodoItem(title="Задача", deadline=future)
        item.change_deadline(None)
        assert item.deadline is None

    def test_deadline_must_be_datetime(self):
        item = TodoItem(title="Задача")
        with pytest.raises(ValueError, match="должен быть datetime"):
            item.change_deadline("2026-12-31")  # type: ignore[arg-type]


# ---------- Статус выполнения ----------

class TestCompletion:

    def test_new_task_is_active(self):
        item = TodoItem(title="Задача")
        assert item.is_completed is False

    def test_mark_as_completed(self):
        item = TodoItem(title="Задача")
        item.mark_as_completed()
        assert item.is_completed is True

    def test_mark_as_active(self):
        item = TodoItem(title="Задача", is_completed=True)
        item.mark_as_active()
        assert item.is_completed is False

    def test_toggle_completion(self):
        item = TodoItem(title="Задача")
        item.toggle_completion()
        assert item.is_completed is True
        item.toggle_completion()
        assert item.is_completed is False


# ---------- Приоритет ----------

class TestPriority:

    def test_default_priority_is_medium(self):
        item = TodoItem(title="Задача")
        assert item.priority == Priority.MEDIUM

    def test_change_priority(self):
        item = TodoItem(title="Задача")
        item.change_priority(Priority.HIGH)
        assert item.priority == Priority.HIGH

    def test_change_priority_to_invalid_type_raises(self):
        item = TodoItem(title="Задача")
        with pytest.raises(ValueError, match="Priority"):
            item.change_priority("Высокий")  # type: ignore[arg-type]

    def test_all_priority_values_exist(self):
        assert Priority.LOW.value == "Низкий"
        assert Priority.MEDIUM.value == "Средний"
        assert Priority.HIGH.value == "Высокий"


# ---------- Присвоение id ----------

class TestIdAssignment:

    def test_new_item_has_no_id(self):
        item = TodoItem(title="Задача")
        assert item.id is None

    def test_assign_id(self):
        item = TodoItem(title="Задача")
        item.assign_id(7)
        assert item.id == 7

    def test_assign_id_twice_raises(self):
        item = TodoItem(title="Задача", item_id=5)
        with pytest.raises(ValueError, match="уже задан"):
            item.assign_id(6)


# ---------- Равенство и хеш ----------

class TestEquality:

    def test_items_with_same_id_are_equal(self):
        a = TodoItem(title="A", item_id=1)
        b = TodoItem(title="B", item_id=1)
        assert a == b

    def test_items_with_different_id_are_not_equal(self):
        a = TodoItem(title="A", item_id=1)
        b = TodoItem(title="B", item_id=2)
        assert a != b

    def test_items_without_id_are_not_equal(self):
        a = TodoItem(title="A")
        b = TodoItem(title="A")
        assert a != b

    def test_hash_works_with_id(self):
        a = TodoItem(title="A", item_id=1)
        b = TodoItem(title="B", item_id=1)
        assert hash(a) == hash(b)
        assert len({a, b}) == 1