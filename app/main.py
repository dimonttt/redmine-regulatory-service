from fastapi import FastAPI

from app import scheduler
from app.api.health import router as health_router
from app.api.runs import router as runs_router
from app.api.suggestions import router as suggestions_router
from app.api.auth import router as auth_router
from app.scheduler import start_scheduler

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