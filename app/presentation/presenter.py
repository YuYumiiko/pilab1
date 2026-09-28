from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.domain.entities import Priority
from app.domain.services import SortMode, TaskFilter, TodoService
from app.presentation.interfaces import ITodoView


_INVALID = object()


class TodoPresenter:

    def __init__(self, view: ITodoView, service: TodoService) -> None:
        self._view = view
        self._service = service

    # Обработчики событий View

    def on_add_task(self) -> None:
        title = self._view.get_task_title_input().strip()
        if not title:
            self._view.show_error("Название задачи не может быть пустым")
            return

        deadline = self._parse_deadline(self._view.get_deadline_input())
        if deadline is _INVALID:
            return

        try:
            priority = Priority(self._view.get_priority_input())
        except ValueError:
            self._view.show_error("Некорректный приоритет")
            return

        try:
            self._service.create_task(title, priority=priority, deadline=deadline)
        except ValueError as exc:
            self._view.show_error(str(exc))
            return

        self._view.clear_input()
        self.refresh()

    def on_toggle_completion(self) -> None:
        task_id = self._view.get_selected_task_id()
        if task_id is None:
            self._view.show_error("Выберите задачу в списке")
            return

        try:
            self._service.toggle_completion(task_id)
        except ValueError as exc:
            self._view.show_error(str(exc))
            return

        self.refresh()

    def on_edit_task(self) -> None:
        task_id = self._view.get_selected_task_id()
        if task_id is None:
            self._view.show_error("Выберите задачу для редактирования")
            return

        current = next(
            (t for t in self._service.get_tasks(TaskFilter.ALL) if t.id == task_id),
            None,
        )
        if current is None:
            self._view.show_error("Задача не найдена")
            return

        deadline_str = (
            current.deadline.strftime("%d.%m.%Y %H:%M")
            if current.deadline
            else ""
        )
        data = self._view.ask_edit_data(
            current.title, current.priority.value, deadline_str
        )
        if data is None:
            return

        new_title = data["title"].strip()
        if not new_title:
            self._view.show_error("Название не может быть пустым")
            return

        try:
            new_priority = Priority(data["priority"])
        except ValueError:
            self._view.show_error("Некорректный приоритет")
            return

        new_deadline = self._parse_deadline(data["deadline"])
        if new_deadline is _INVALID:
            return

        try:
            self._service.update_task(task_id, new_title, new_priority, new_deadline)
        except ValueError as exc:
            self._view.show_error(str(exc))
            return

        self.refresh()

    def on_delete_task(self) -> None:
        task_id = self._view.get_selected_task_id()
        if task_id is None:
            self._view.show_error("Выберите задачу для удаления")
            return

        self._service.delete_task(task_id)
        self.refresh()

    def on_clear_completed(self) -> None:
        removed = self._service.clear_completed()
        if removed == 0:
            self._view.show_info("Нет выполненных задач для очистки")
        self.refresh()

    def on_filter_changed(self) -> None:
        """Смена фильтра или режима сортировки."""
        self.refresh()

    # Обновление View

    def refresh(self) -> None:
        """Перечитать данные из сервиса и перерисовать View."""
        # Фильтр по статусу
        try:
            task_filter = TaskFilter(self._view.get_current_filter())
        except ValueError:
            task_filter = TaskFilter.ALL

        # Режим сортировки
        try:
            sort_mode = SortMode(self._view.get_sort_mode())
        except ValueError:
            sort_mode = SortMode.BY_CREATED

        # Получаем задачи и обновляем таблицу
        tasks = self._service.get_tasks(task_filter, sort_mode)
        self._view.show_tasks(tasks)

        # Статистика (без учёта фильтров)
        stats = self._service.get_statistics()
        self._view.update_statistics(
            total=stats["total"],
            active=stats["active"],
            completed=stats["completed"],
        )

    # Приватные хелперы

    def _parse_deadline(self, raw: str):
        """Вернуть datetime / None (пусто) / _INVALID (ошибка формата)."""
        raw = raw.strip()
        if not raw:
            return None
        try:
            return datetime.strptime(raw, "%d.%m.%Y %H:%M")
        except ValueError:
            self._view.show_error(
                "Неверный формат дедлайна. Ожидается ДД.ММ.ГГГГ ЧЧ:ММ"
            )
            return _INVALID