from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.regulatory_work import RegulatoryWork
from app.models.work_history import WorkHistory


def select_works_for_client(
    db: Session,
    client_id: int,
    target_hours: float,
    period_year: int,
    period_month: int,
) -> list[dict]:
    """
    Подбирает типовые работы для клиента так, чтобы их суммарная трудоёмкость
    была примерно равна target_hours. Исключает работы, которые уже выполнялись
    у этого клиента за указанный период.
    """
    period_start = date(period_year, period_month, 1)
    if period_month == 12:
        period_end = date(period_year + 1, 1, 1)
    else:
        period_end = date(period_year, period_month + 1, 1)

    # Работы, которые уже выполнялись у этого клиента в этом периоде
    already_done_ids = set(
        db.execute(
            select(WorkHistory.regulatory_work_id)
            .where(WorkHistory.client_id == client_id)
            .where(WorkHistory.regulatory_work_id.isnot(None))
            .where(WorkHistory.spent_on >= period_start)
            .where(WorkHistory.spent_on < period_end)
        ).scalars().all()
    )

    # Все активные работы, кроме уже выполненных
    works = db.execute(
        select(RegulatoryWork)
        .where(RegulatoryWork.is_active.is_(True))
        .order_by(RegulatoryWork.estimated_hours.desc())
    ).scalars().all()

    candidates = [w for w in works if w.id not in already_done_ids]

    # Жадный подбор: берём работы от самых крупных, пока не наберём target_hours
    selected = []
    accumulated = 0.0
    for w in candidates:
        if accumulated >= target_hours:
            break
        selected.append(w)
        accumulated += float(w.estimated_hours)

    return [
        {
            "id": w.id,
            "code": w.code,
            "name": w.name,
            "description": w.description,
            "category": w.category,
            "estimated_hours": float(w.estimated_hours),
            "reason": f"Восполнение недостатка часов по клиенту",
        }
        for w in selected
    ]