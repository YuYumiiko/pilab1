from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Системные"], summary="Проверка состояния")
def health_check() -> dict:
    return {"status": "ok"}

@router.get("/", tags=["Системные"], summary="Корневой путь")
def root() -> dict:
    return {
        "service": "Todo List",
        "docs": "/docs",
        "health": "/health",
    }