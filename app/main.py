from fastapi import FastAPI

from app.config import settings


app = FastAPI(
    title="Redmine Regulatory Works Service",
    description="Сервис анализа трудозатрат и подбора регламентных работ",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "redmine_url": settings.redmine_url,
    }