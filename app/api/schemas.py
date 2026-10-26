from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.domain.entities import Priority, MAX_TITLE_LENGTH
from enum import Enum

class TaskFilter(str, Enum):
    ALL = "all"
    ACTIVE = "active"
    COMPLETED = "completed"

class TaskSort(str, Enum):
    CREATED_AT_ASC = "created_at"
    CREATED_AT_DESC = "-created_at"
    TITLE_ASC = "title"
    TITLE_DESC = "-title"
    PRIORITY_ASC = "priority"
    PRIORITY_DESC = "-priority"
    DEADLINE_ASC = "deadline"
    DEADLINE_DESC = "-deadline"

class TodoResponseSchema(BaseModel):
    id: int
    title: str
    is_completed: bool
    priority: Priority
    created_at: datetime
    deadline: datetime | None

    model_config = ConfigDict(from_attributes=True)

class TodoCreateSchema(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=MAX_TITLE_LENGTH,
        description="Название задачи",
        examples=["Купить хлеб"],
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Приоритет задачи",
    )
    deadline: datetime | None = Field(
        default=None,
        description="Дата дедлайна (необязательно)",
    )

class TodoUpdateSchema(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=MAX_TITLE_LENGTH,
        description="Новое название",
    )
    priority: Priority | None = Field(
        default=None,
        description="Новый приоритет",
    )
    deadline: datetime | None = Field(
        default=None,
        description="Новый дедлайн. Передать null, чтобы убрать",
    )

class TaskFilter(str, Enum):
    ALL = "all"
    ACTIVE = "active"
    COMPLETED = "completed"