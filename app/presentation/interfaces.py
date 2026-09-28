from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities import Priority, TodoItem


class ITodoView(ABC):

    # ---------- Методы, которые Presenter вызывает у View ----------

    @abstractmethod
    def show_tasks(self, tasks: List[TodoItem]) -> None:
        """Отобразить список задач."""

    @abstractmethod
    def show_error(self, message: str) -> None:
        """Показать сообщение об ошибке."""

    @abstractmethod
    def show_info(self, message: str) -> None:
        """Показать информационное сообщение."""

    @abstractmethod
    def clear_input(self) -> None:
        """Очистить поле ввода названия задачи."""

    @abstractmethod
    def update_statistics(self, total: int, active: int, completed: int) -> None:
        """Обновить строку статистики."""

    # ---------- Методы, через которые View сообщает данные Presenter'у ----------

    @abstractmethod
    def get_task_title_input(self) -> str:
        """Получить введённое название задачи."""

    @abstractmethod
    def get_selected_task_id(self) -> Optional[int]:
        """Получить id выделенной в таблице задачи (None, если ничего не выбрано)."""

    @abstractmethod
    def get_current_filter(self) -> str:
        """Получить текущий фильтр ('all' / 'active' / 'completed')."""

    @abstractmethod
    def get_deadline_input(self) -> str:
        """Получить введённый дедлайн (или пустую строку)."""

    @abstractmethod
    def get_priority_input(self) -> str:
        """Получить выбранный приоритет из формы создания."""

    @abstractmethod
    def ask_edit_data(
            self, title: str, priority: str, deadline: str
    ) -> Optional[dict]:
        """
        Открыть диалог редактирования.
        Возвращает dict {'title': str, 'priority': str, 'deadline': str} или None (отмена).
        """

    @abstractmethod
    def get_sort_mode(self) -> str:
        """Получить текущий режим сортировки ('by_created' / 'by_priority' / 'by_deadline')."""
