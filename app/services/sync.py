from datetime import date

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.work_history import WorkHistory
from app.redmine.client import redmine_client
from app.models.monthly_aggregate import MonthlyAggregate
from sqlalchemy import func

def sync_clients(db: Session) -> dict:
    # Синхронизирует проекты Redmine в таблицу clients
    projects = redmine_client.get_projects_all()
    created = 0
    updated = 0

    for project in projects:
        stmt = select(Client).where(Client.redmine_project_id == project["id"])
        existing = db.execute(stmt).scalar_one_or_none()

        if existing is None:
            db.add(
                Client(
                    redmine_project_id=project["id"],
                    name=project["name"],
                    identifier=project.get("identifier"),
                    is_active=(project.get("status", 1) == 1),
                )
            )
            created += 1
        else:
            existing.name = project["name"]
            existing.identifier = project.get("identifier")
            existing.is_active = project.get("status", 1) == 1
            updated += 1

    db.commit()
    return {"created": created, "updated": updated, "total": len(projects)}


def sync_time_entries(
    db: Session,
    from_date: date | None = None,
    to_date: date | None = None,
) -> dict:
    # Синхронизирует трудозатраты Redmine в work_history
    entries = redmine_client.get_time_entries_all(from_date=from_date, to_date=to_date)
    created = 0
    skipped = 0
    deleted = 0
    updated = 0

    redmine_ids = {entry["id"] for entry in entries}

    stmt = select(WorkHistory)
    if from_date:
        stmt = stmt.where(WorkHistory.spent_on >= from_date)
    if to_date:
        stmt = stmt.where(WorkHistory.spent_on <= to_date)
    
    local_entries = db.execute(stmt).scalars().all()

    #  если в Redmine удалили
    for local in local_entries:
        if local.redmine_time_entry_id not in redmine_ids:
            db.delete(local)
            deleted += 1

    # добавление и обновление
    for entry in entries:
        stmt_check = select(WorkHistory).where(
            WorkHistory.redmine_time_entry_id == entry["id"]
        )
        existing = db.execute(stmt_check).scalar_one_or_none()

        activity = entry.get("activity") or {}
        activity_name = activity.get("name")
        
        hours = float(entry["hours"])
        spent_on = entry["spent_on"]

        if existing is not None:
            hours_changed = f"{float(existing.hours):.2f}" != f"{hours:.2f}"
            date_changed = str(existing.spent_on) != str(spent_on)
            activity_changed = str(existing.activity) != str(activity_name)

            if hours_changed or date_changed or activity_changed:
                existing.hours = hours
                existing.spent_on = spent_on
                existing.activity = activity_name
                updated += 1
            else:
                skipped += 1
            continue

        project_id = entry["project"]["id"]
        client = db.execute(
            select(Client).where(Client.redmine_project_id == project_id)
        ).scalar_one_or_none()
        if client is None:
            skipped += 1
            continue

        issue = entry.get("issue") or {}

        db.add(
            WorkHistory(
                client_id=client.id,
                regulatory_work_id=None,
                redmine_issue_id=issue.get("id"),
                redmine_time_entry_id=entry["id"],
                subject=None,
                hours=hours,
                spent_on=spent_on,
                activity=activity_name,
            )
        )
        created += 1

    db.commit()
    return {
        "created": created,
        "skipped": skipped,
        "deleted": deleted,
        "updated": updated,
        "total": len(entries),
    }


def sync_monthly_aggregates(db: Session, period_year: int, period_month: int) -> dict:
    # Пересчитывает сумму часов за месяц для всех клиентов
    # Удаляем старые агрегаты за этот месяц
    db.execute(
        delete(MonthlyAggregate)
        .where(MonthlyAggregate.period_year == period_year)
        .where(MonthlyAggregate.period_month == period_month)
    )

    from datetime import date
    period_start = date(period_year, period_month, 1)
    if period_month == 12:
        period_end = date(period_year + 1, 1, 1)
    else:
        period_end = date(period_year, period_month + 1, 1)

    # Группируем часы по клиентам за период
    results = db.execute(
        select(
            WorkHistory.client_id,
            func.sum(WorkHistory.hours).label("total_hours")
        )
        .where(WorkHistory.spent_on >= period_start)
        .where(WorkHistory.spent_on < period_end)
        .group_by(WorkHistory.client_id)
    ).all()

    for client_id, total_hours in results:
        db.add(
            MonthlyAggregate(
                client_id=client_id,
                period_year=period_year,
                period_month=period_month,
                total_hours=float(total_hours or 0),
            )
        )
    db.commit()
    return {"aggregated_clients": len(results)}