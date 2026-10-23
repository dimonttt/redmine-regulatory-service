from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import RunCreate, RunResponse
from app.db import get_db
from app.models.calculation_run import CalculationRun
from app.services.orchestrator import run_calculation


router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.post("", response_model=dict)
def create_run(payload: RunCreate, db: Session = Depends(get_db)):
    #запуск полного расчета за указанный месяц
    try:
        result = run_calculation(
            db,
            period_year=payload.period_year,
            period_month=payload.period_month,
            trigger_type="MANUAL",
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list[RunResponse])
def list_runs(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    #возврат списока запусков расчета (последние сверху)
    stmt = (
        select(CalculationRun)
        .order_by(CalculationRun.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.execute(stmt).scalars().all()


@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):
    # возврат информации о конкретном запуске
    run = db.execute(
        select(CalculationRun).where(CalculationRun.id == run_id)
    ).scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run