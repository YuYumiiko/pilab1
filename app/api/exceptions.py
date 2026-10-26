from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import TodoNotFoundError

async def domain_value_error_handler(
    request: Request, exc: ValueError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": str(exc),
            "path": request.url.path
        },
    )

async def not_found_error_handler(
    request: Request, exc: TodoNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc),
            "path": request.url.path
        }
    )