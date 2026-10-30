from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.work_history import WorkHistory
from app.redmine.client import redmine_client


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
    # cинхронизирует трудозатраты Redmine в work_history
    entries = redmine_client.get_time_entries_all(from_date=from_date, to_date=to_date)
    created = 0
    skipped = 0
    deleted = 0

    redmine_ids = {entry["id"] for entry in entries}

    # поиск всех записей в БД за период
    stmt = select(WorkHistory)
    if from_date:
        stmt = stmt.where(WorkHistory.spent_on >= from_date)
    if to_date:
        stmt = stmt.where(WorkHistory.spent_on <= to_date)
    
    local_entries = db.execute(stmt).scalars().all()

    # удаление, если запись есть у нас, но её нет в Redmine
    for local in local_entries:
        if local.redmine_time_entry_id not in redmine_ids:
            db.delete(local)
            deleted += 1

    # добавление, если записи нет у нас, но есть в Redmine
    for entry in entries:
        stmt_check = select(WorkHistory).where(
            WorkHistory.redmine_time_entry_id == entry["id"]
        )
        if db.execute(stmt_check).scalar_one_or_none() is not None:
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
        activity = entry.get("activity") or {}

        db.add(
            WorkHistory(
                client_id=client.id,
                regulatory_work_id=None,
                redmine_issue_id=issue.get("id"),
                redmine_time_entry_id=entry["id"],
                subject=None,
                hours=entry["hours"],
                spent_on=entry["spent_on"],
                activity=activity.get("name"),
            )
        )
        created += 1

    db.commit()
    return {
        "created": created,
        "skipped": skipped,
        "deleted": deleted,
        "total": len(entries),
    }