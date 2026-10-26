from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database import Base
from app.domain.entities import MAX_TITLE_LENGTH, Priority


class TodoModel(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(MAX_TITLE_LENGTH), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    priority: Mapped[Priority] = mapped_column(
        Enum(
            Priority,
            values_callable = lambda enum_cls:[e.value for e in enum_cls]
        ),
            nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

