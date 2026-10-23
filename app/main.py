from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.runs import router as runs_router
from app.api.suggestions import router as suggestions_router


app = FastAPI(
    title="Redmine Regulatory Works Service",
    description="Сервис анализа трудозатрат и подбора регламентных работ",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(runs_router)
app.include_router(suggestions_router)


@app.get("/")
def root():
    return {"service": "redmine-regulatory-service", "version": "0.1.0"}