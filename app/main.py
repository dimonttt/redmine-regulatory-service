from fastapi import FastAPI

from app import scheduler
from app.api.health import router as health_router
from app.api.runs import router as runs_router
from app.api.suggestions import router as suggestions_router
from app.api.auth import router as auth_router
from app.scheduler import start_scheduler
from app.services.email_sender import send_report_email
from app.services.calculation import calculate_client_hours
from app.models.suggestion import Suggestion
from sqlalchemy import select
from app.db import SessionLocal

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(
    title="Redmine Regulatory Works Service",
    description="Сервис анализа трудозатрат и подбора регламентных работ",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(runs_router)
app.include_router(suggestions_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"service": "redmine-regulatory-service", "version": "0.1.0"}

@app.get("/test-scheduler")
def test_scheduler():
    from app.scheduler import scheduled_run
    scheduled_run()
    return {"status": "scheduler executed"}


@app.get("/api/send-report")
def send_manual_report(period_year: int = 2026, period_month: int = 10):
    # формирование и отправка отчета на почту
    db = SessionLocal()
    try:
        # последний запуск за указанный период (или создание нового)
        calc_results = calculate_client_hours(db, period_year, period_month)
        clients_data = []
        
        for r in calc_results:
            # поиск предложения для клиента
            suggestions = db.execute(
                select(Suggestion)
                .where(Suggestion.client_id == r["client_id"])
                .order_by(Suggestion.id.desc())
                .limit(10)
            ).scalars().all()
            
            clients_data.append({
                "name": r["client_name"],
                "planned_hours": r["planned_hours"],
                "actual_hours": r["actual_hours"],
                "deficit_hours": r["deficit_hours"],
                "below_threshold": r["below_threshold"],
                "suggestions": [
                    {"title": s.title, "estimated_hours": s.estimated_hours, "reason": s.reason}
                    for s in suggestions
                ],
            })
        
        success = send_report_email(period_year, period_month, clients_data)
        return {"status": "sent" if success else "failed"}
    finally:
        db.close()