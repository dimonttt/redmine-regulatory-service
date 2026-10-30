from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.planned_hours import PlannedHours
from app.models.work_history import WorkHistory

# считает фактические часы по каждому клиенту за указанный месяц
# возвращает список клиентов с недостатком
def calculate_client_hours(
    db: Session,
    period_year: int,
    period_month: int,
) -> list[dict]:
    period_start = date(period_year, period_month, 1)
    if period_month == 12:
        period_end = date(period_year + 1, 1, 1)
    else:
        period_end = date(period_year, period_month + 1, 1)

    actual_subq = (
        select(
            WorkHistory.client_id,
            func.coalesce(func.sum(WorkHistory.hours), 0).label("actual_hours"),
        )
        .where(WorkHistory.spent_on >= period_start)
        .where(WorkHistory.spent_on < period_end)
        .group_by(WorkHistory.client_id)
        .subquery()
    )

    stmt = (
        select(
            Client.id,
            Client.name,
            Client.redmine_project_id,
            func.coalesce(actual_subq.c.actual_hours, 0).label("actual_hours"),
            PlannedHours.planned_hours,
            PlannedHours.threshold_hours,
        )
        .join(PlannedHours, PlannedHours.client_id == Client.id)
        .outerjoin(actual_subq, actual_subq.c.client_id == Client.id)
        .where(PlannedHours.period_year == period_year)
        .where(PlannedHours.period_month == period_month)
        .where(Client.is_active.is_(True))
        .order_by(Client.name)
    )

    rows = db.execute(stmt).all()

    results = []
    for row in rows:
        actual = float(row.actual_hours or 0)
        planned = float(row.planned_hours)
        threshold = float(row.threshold_hours or 0)
        deficit = planned - actual

        results.append(
            {
                "client_id": row.id,
                "client_name": row.name,
                "redmine_project_id": row.redmine_project_id,
                "planned_hours": planned,
                "actual_hours": actual,
                "deficit_hours": deficit,
                "threshold_hours": threshold,
                "below_threshold": deficit > threshold,
            }
        )

    return results