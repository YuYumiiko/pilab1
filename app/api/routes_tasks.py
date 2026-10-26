from __future__ import annotations

from fastapi import APIRouter, Depends, status, Path, Response, Query

from app.api.dependencies import get_service
from app.api.schemas import TodoResponseSchema, TodoCreateSchema, TodoUpdateSchema, TaskFilter, TaskSort
from app.domain.services import TodoService

router = APIRouter(prefix="/api/tasks", tags=["Работа с задачами"])

@router.get(
    "",
    response_model=list[TodoResponseSchema],
    summary="Получить список задач",
)
def get_tasks(
        filter_mode: TaskFilter = Query(TaskFilter.ALL, alias="filter"),
        sort: TaskSort = Query(TaskSort.CREATED_AT_ASC),
        service: TodoService = Depends(get_service)
) -> list[TodoResponseSchema]:
    items = service.get_todos(
        filter_mode=filter_mode.value,
        sort=sort.value,
    )
    return [TodoResponseSchema.model_validate(item) for item in items]

@router.get(
    "/{id}",
    response_model=TodoResponseSchema,
    summary="Получить задачу"
)
def get_task_by_id(
    id: int = Path(..., ge=1, description="ID задачи"),
    service: TodoService = Depends(get_service)
) -> TodoResponseSchema:
    item = service.get_todo(id)
    return TodoResponseSchema.model_validate(item)

@router.post(
    "",
    response_model=TodoResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать задачу"
)
def create_task(
    payload: TodoCreateSchema,
    service: TodoService = Depends(get_service)
) -> TodoResponseSchema:
    item = service.create_todo(
        title=payload.title,
        priority=payload.priority,
        deadline=payload.deadline,
    )
    return TodoResponseSchema.model_validate(item)

@router.patch(
    "/{id}",
    response_model=TodoResponseSchema,
    summary="Изменить задачу"
)
def patch_task(
    payload: TodoUpdateSchema,
    id: int = Path(..., ge=1, description="ID задачи"),
    service: TodoService = Depends(get_service)
) -> TodoResponseSchema:
    data = payload.model_dump(exclude_unset=True)
    item = service.edit_todo(
        id,
        title=data.get("title"),
        priority=data.get("priority"),
        deadline=data.get("deadline"),
        update_deadline="deadline" in data,
    )
    return TodoResponseSchema.model_validate(item)

@router.post(
    "/{id}/toggle",
    response_model=TodoResponseSchema,
    summary="Переключить статус задачи",
)
def toggle_task(
    id: int = Path(..., ge=1, description="ID задачи"),
    service: TodoService = Depends(get_service),
) -> TodoResponseSchema:
    item = service.toggle_completed(id)
    return TodoResponseSchema.model_validate(item)

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить задачу"
)
def delete_task_by_id(
    id: int = Path(..., ge=1, description="ID задачи"),
    service: TodoService = Depends(get_service)
) -> Response:
    service.delete_todo(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить все неактивные задачи",
)
def clear_completed_tasks(
    service: TodoService = Depends(get_service),
) -> Response:
    service.clear_completed()
    return Response(status_code=status.HTTP_204_NO_CONTENT)