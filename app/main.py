from fastapi import FastAPI

from app.api.health import router as health_router


app = FastAPI(
    title="Redmine Regulatory Works Service",
    description="Сервис анализа трудозатрат и подбора регламентных работ",
    version="0.1.0",
)

app.include_router(health_router)


@app.get("/")
def root():
    return {"service": "redmine-regulatory-service", "version": "0.1.0"}