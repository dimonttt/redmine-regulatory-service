from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import (
    CreatedTaskResponse,
    SuggestionResponse,
    SuggestionStatusResponse,
)
from app.db import get_db
from app.models.suggestion import Suggestion
from app.services.task_creator import create_task_from_suggestion


router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


@router.get("", response_model=list[SuggestionResponse])
def list_suggestions(
    run_id: int | None = None,
    client_id: int | None = None,
    status: str | None = None,
    source: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    # возврат списка предложений с фильтрами
    stmt = select(Suggestion).order_by(Suggestion.id)
    if run_id is not None:
        stmt = stmt.where(Suggestion.calculation_run_id == run_id)
    if client_id is not None:
        stmt = stmt.where(Suggestion.client_id == client_id)
    if status is not None:
        stmt = stmt.where(Suggestion.status == status)
    if source is not None:     
        stmt = stmt.where(Suggestion.source == source)
    stmt = stmt.limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


@router.get("/{suggestion_id}", response_model=SuggestionResponse)
def get_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    s = db.execute(
        select(Suggestion).where(Suggestion.id == suggestion_id)
    ).scalar_one_or_none()
    if s is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return s


@router.post("/{suggestion_id}/approve", response_model=SuggestionStatusResponse)
def approve_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    # смена статуса предложения на APPROVED
    s = db.execute(
        select(Suggestion).where(Suggestion.id == suggestion_id)
    ).scalar_one_or_none()
    if s is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    if s.status not in ("NEW", "APPROVED", "REJECTED"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve suggestion with status={s.status}",
        )
    s.status = "APPROVED"
    db.commit()
    db.refresh(s)
    return s


@router.post("/{suggestion_id}/reject", response_model=SuggestionStatusResponse)
def reject_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    # смена статуса предложения на REJECTED
    s = db.execute(
        select(Suggestion).where(Suggestion.id == suggestion_id)
    ).scalar_one_or_none()
    if s is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    if s.status == "CREATED":
        raise HTTPException(
            status_code=400,
            detail="Cannot reject suggestion that was already created in Redmine",
        )
    s.status = "REJECTED"
    db.commit()
    db.refresh(s)
    return s


@router.post("/{suggestion_id}/create-task", response_model=dict)
def create_task(suggestion_id: int, db: Session = Depends(get_db)):
    # создание задачи в Redmine по предложению
    try:
        result = create_task_from_suggestion(db, suggestion_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))