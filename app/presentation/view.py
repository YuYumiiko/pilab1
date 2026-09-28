from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Optional

from app.domain.entities import TodoItem
from app.presentation.interfaces import ITodoView


# Человекочитаемые названия режимов сортировки ↔ внутренние коды
_SORT_LABELS = {
    "По дате создания": "by_created",
    "По приоритету": "by_priority",
    "По дедлайну": "by_deadline",
}
_SORT_LABELS_REVERSE = {v: k for k, v in _SORT_LABELS.items()}


class TodoView(tk.Tk, ITodoView):

    def __init__(self) -> None:
        super().__init__()
        self.title("Todo List — MVP")
        self.geometry("960x560")
        self.minsize(800, 480)

        self._presenter = None
        self._build_ui()

    def set_presenter(self, presenter) -> None:
        self._presenter = presenter

    # ---------- Построение интерфейса ----------

    def _build_ui(self) -> None:
        # ===== Верхняя панель: ввод названия + приоритет + кнопка =====
        top = ttk.Frame(self, padding=8)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Задача:").pack(side=tk.LEFT)
        self._entry = ttk.Entry(top, width=40)
        self._entry.pack(side=tk.LEFT, padx=6, fill=tk.X, expand=True)
        self._entry.bind("<Return>", lambda _e: self._on_add())

        ttk.Label(top, text="Приоритет:").pack(side=tk.LEFT, padx=(10, 0))
        self._priority_var = tk.StringVar(value="Средний")
        priority_box = ttk.Combobox(
            top,
            textvariable=self._priority_var,
            values=["Низкий", "Средний", "Высокий"],
            state="readonly",
            width=10,
        )
        priority_box.pack(side=tk.LEFT, padx=6)

        ttk.Button(top, text="Добавить", command=self._on_add).pack(side=tk.LEFT)

        # ===== Панель дедлайна =====
        dl = ttk.Frame(self, padding=(8, 0, 8, 8))
        dl.pack(fill=tk.X)
        ttk.Label(dl, text="Дедлайн (ДД.ММ.ГГГГ ЧЧ:ММ):").pack(side=tk.LEFT)
        self._deadline_entry = ttk.Entry(dl, width=22)
        self._deadline_entry.pack(side=tk.LEFT, padx=6)

        # ===== Панель фильтров, сортировки и операций =====
        mid = ttk.Frame(self, padding=(8, 0, 8, 8))
        mid.pack(fill=tk.X)

        ttk.Label(mid, text="Фильтр:").pack(side=tk.LEFT)
        self._filter_var = tk.StringVar(value="all")
        filter_box = ttk.Combobox(
            mid,
            textvariable=self._filter_var,
            values=["all", "active", "completed"],
            state="readonly",
            width=12,
        )
        filter_box.pack(side=tk.LEFT, padx=6)
        filter_box.bind("<<ComboboxSelected>>", lambda _e: self._on_filter_changed())

        ttk.Label(mid, text="Сортировка:").pack(side=tk.LEFT, padx=(10, 0))
        self._sort_var = tk.StringVar(value="По дате создания")
        sort_box = ttk.Combobox(
            mid,
            textvariable=self._sort_var,
            values=list(_SORT_LABELS.keys()),
            state="readonly",
            width=18,
        )
        sort_box.pack(side=tk.LEFT, padx=6)
        sort_box.bind("<<ComboboxSelected>>", lambda _e: self._on_filter_changed())

        # Кнопки операций
        ttk.Button(
            mid, text="Выполнить / вернуть", command=self._on_toggle
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            mid, text="Редактировать", command=self._on_edit
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            mid, text="Удалить", command=self._on_delete
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            mid, text="Очистить завершённые", command=self._on_clear_completed
        ).pack(side=tk.RIGHT)

        # ===== Таблица задач =====
        table_frame = ttk.Frame(self, padding=(8, 0, 8, 0))
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "title", "status", "priority", "created", "deadline")
        self._tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        headers = {
            "id": "ID",
            "title": "Задача",
            "status": "Статус",
            "priority": "Приоритет",
            "created": "Создана",
            "deadline": "Дедлайн",
        }
        widths = {
            "id": 50,
            "title": 320,
            "status": 100,
            "priority": 100,
            "created": 140,
            "deadline": 140,
        }
        for col in columns:
            self._tree.heading(col, text=headers[col])
            self._tree.column(col, width=widths[col], anchor=tk.W)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(
            table_frame, orient="vertical", command=self._tree.yview
        )
        self._tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._tree.bind("<Double-1>", lambda _e: self._on_toggle())

        # ===== Строка статистики =====
        self._status = ttk.Label(self, anchor=tk.W, padding=6, relief=tk.SUNKEN)
        self._status.pack(fill=tk.X, side=tk.BOTTOM)

    # ---------- Делегирование презентеру ----------

    def _on_add(self) -> None:
        self._presenter.on_add_task()

    def _on_toggle(self) -> None:
        self._presenter.on_toggle_completion()

    def _on_edit(self) -> None:
        self._presenter.on_edit_task()

    def _on_delete(self) -> None:
        self._presenter.on_delete_task()

    def _on_clear_completed(self) -> None:
        self._presenter.on_clear_completed()

    def _on_filter_changed(self) -> None:
        self._presenter.on_filter_changed()

    # ---------- Реализация ITodoView ----------

    def show_tasks(self, tasks: List[TodoItem]) -> None:
        for row in self._tree.get_children():
            self._tree.delete(row)

        for item in tasks:
            status = "Выполнена" if item.is_completed else "Активна"
            created = item.created_at.strftime("%d.%m.%Y %H:%M")
            deadline = (
                item.deadline.strftime("%d.%m.%Y %H:%M")
                if item.deadline
                else "—"
            )
            self._tree.insert(
                "",
                tk.END,
                iid=str(item.id),
                values=(
                    item.id,
                    item.title,
                    status,
                    item.priority.value,
                    created,
                    deadline,
                ),
            )

    def show_error(self, message: str) -> None:
        messagebox.showerror("Ошибка", message)

    def show_info(self, message: str) -> None:
        messagebox.showinfo("Информация", message)

    def clear_input(self) -> None:
        self._entry.delete(0, tk.END)
        self._deadline_entry.delete(0, tk.END)
        self._priority_var.set("Средний")

    def update_statistics(self, total: int, active: int, completed: int) -> None:
        self._status.config(
            text=(
                f"Всего: {total}    "
                f"Активных: {active}    "
                f"Выполнено: {completed}"
            )
        )

    def get_task_title_input(self) -> str:
        return self._entry.get()

    def get_deadline_input(self) -> str:
        return self._deadline_entry.get()

    def get_priority_input(self) -> str:
        return self._priority_var.get()

    def get_sort_mode(self) -> str:
        """Вернуть код режима сортировки (by_created / by_priority / by_deadline)."""
        label = self._sort_var.get()
        return _SORT_LABELS.get(label, "by_created")

    def get_selected_task_id(self) -> Optional[int]:
        selection = self._tree.selection()
        if not selection:
            return None
        return int(selection[0])

    def get_current_filter(self) -> str:
        return self._filter_var.get()

    # ---------- Диалог редактирования ----------

    def ask_edit_data(
        self, title: str, priority: str, deadline: str
    ) -> Optional[dict]:
        """Модальный диалог редактирования задачи."""
        dialog = tk.Toplevel(self)
        dialog.title("Редактирование задачи")
        dialog.geometry("460x210")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)

        result: dict = {"value": None}
        dialog.columnconfigure(1, weight=1)

        ttk.Label(dialog, text="Название:").grid(
            row=0, column=0, padx=10, pady=(14, 6), sticky=tk.W
        )
        title_var = tk.StringVar(value=title)
        ttk.Entry(dialog, textvariable=title_var, width=34).grid(
            row=0, column=1, padx=10, pady=(14, 6), sticky=tk.EW
        )

        ttk.Label(dialog, text="Приоритет:").grid(
            row=1, column=0, padx=10, pady=6, sticky=tk.W
        )
        prio_var = tk.StringVar(value=priority or "Средний")
        ttk.Combobox(
            dialog,
            textvariable=prio_var,
            values=["Низкий", "Средний", "Высокий"],
            state="readonly",
            width=32,
        ).grid(row=1, column=1, padx=10, pady=6, sticky=tk.EW)

        ttk.Label(dialog, text="Дедлайн (ДД.ММ.ГГГГ ЧЧ:ММ):").grid(
            row=2, column=0, padx=10, pady=6, sticky=tk.W
        )
        dl_var = tk.StringVar(value=deadline)
        ttk.Entry(dialog, textvariable=dl_var, width=34).grid(
            row=2, column=1, padx=10, pady=6, sticky=tk.EW
        )

        def on_ok() -> None:
            result["value"] = {
                "title": title_var.get(),
                "priority": prio_var.get(),
                "deadline": dl_var.get(),
            }
            dialog.destroy()

        def on_cancel() -> None:
            dialog.destroy()

        btns = ttk.Frame(dialog)
        btns.grid(row=3, column=0, columnspan=2, pady=(14, 12))
        ttk.Button(btns, text="OK", command=on_ok, width=12).pack(
            side=tk.LEFT, padx=6
        )
        ttk.Button(btns, text="Отмена", command=on_cancel, width=12).pack(
            side=tk.LEFT, padx=6
        )

        dialog.bind("<Return>", lambda _e: on_ok())
        dialog.bind("<Escape>", lambda _e: on_cancel())

        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 3
        dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")

        dialog.wait_window()
        return result["value"]