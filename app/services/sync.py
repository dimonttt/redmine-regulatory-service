from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.work_history import WorkHistory
from app.redmine.client import redmine_client


def sync_clients(db: Session) -> dict:
    # синхронизация проектов Redmine в таблицу clients
    data = redmine_client.get_projects()
    created = 0
    updated = 0

    for project in data["projects"]:
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
    return {"created": created, "updated": updated, "total": data["total_count"]}


def sync_time_entries(
    db: Session,
    from_date: date | None = None,
    to_date: date | None = None,
) -> dict:
    # синхронизизация трудозатрат Redmine в work_history
    entries = redmine_client.get_time_entries_all(from_date=from_date, to_date=to_date)
    created = 0
    skipped = 0

    for entry in entries:
        stmt = select(WorkHistory).where(
            WorkHistory.redmine_time_entry_id == entry["id"]
        )
        if db.execute(stmt).scalar_one_or_none() is not None:
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
    return {"created": created, "skipped": skipped, "total": len(entries)}