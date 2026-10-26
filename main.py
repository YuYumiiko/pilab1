import logging

from fastapi import FastAPI, Request

from app.api.routes import router as system_router
from app.api.routes_tasks import router as tasks_router
from app.api import dependencies
from app.api.exceptions import domain_value_error_handler, not_found_error_handler
from app.domain.exceptions import TodoNotFoundError


#Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("todo")

#Приложение
app = FastAPI(
    title="Todo List",
    version="1.69.0"
)

#Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("→ %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info(
        "← %s %s → %d",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response

#Обработчик исключений
app.add_exception_handler(TodoNotFoundError, not_found_error_handler)
app.add_exception_handler(ValueError, domain_value_error_handler)

#Подключаем роутеры
app.include_router(system_router)
app.include_router(tasks_router)