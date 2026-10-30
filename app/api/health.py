from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db


router = APIRouter(tags=["health"])


@router.get("/health/live")
def liveness():
    # liveness - процесс жив и отвечает
    return {"status": "ok"}


@router.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    # readiness - проверяем зависимости БД, Redmine, LLM
    checks = {
        "database": _check_database(db),
        "redmine": _check_redmine(),
        "llm": _check_llm(),
    }
    all_ok = all(c["status"] == "ok" for c in checks.values())
    status_code = 200 if all_ok else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if all_ok else "degraded",
            "checks": checks,
        },
    )


def _check_database(db: Session) -> dict:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "fail", "error": str(e)}


def _check_redmine() -> dict:
    if not settings.redmine_url or not settings.redmine_api_key:
        return {"status": "fail", "error": "redmine_url or api_key not configured"}
    return {"status": "ok", "url": settings.redmine_url}


def _check_llm() -> dict:
    if not settings.llm_base_url or not settings.llm_model:
        return {"status": "fail", "error": "llm not configured"}
    return {"status": "ok", "model": settings.llm_model}