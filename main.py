from __future__ import annotations

from app.data.database import init_db
from app.data.repository import SqlAlchemyTodoRepository
from app.domain.services import TodoService
from app.presentation.presenter import TodoPresenter
from app.presentation.view import TodoView


def main() -> None:
    init_db()

    repository = SqlAlchemyTodoRepository()
    service = TodoService(repository)

    view = TodoView()
    presenter = TodoPresenter(view, service)
    view.set_presenter(presenter)

    presenter.refresh()

    view.mainloop()


if __name__ == "__main__":
    main()