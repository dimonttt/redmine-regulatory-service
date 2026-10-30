from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.created_task import CreatedTask
from app.models.suggestion import Suggestion
from app.redmine.client import redmine_client


def create_task_from_suggestion(db: Session, suggestion_id: int) -> dict:

    # создание задачи в Redmine на основе одобренного предложения
    # защита от дублей через таблицу created_tasks

    suggestion = db.execute(
        select(Suggestion).where(Suggestion.id == suggestion_id)
    ).scalar_one_or_none()
    if suggestion is None:
        raise ValueError(f"Предложение с id={suggestion_id} не найдено")

    if suggestion.status == "REJECTED":
        raise ValueError("Нельзя создать задачу по отклонённому предложению")

    # Проверка: не создана ли уже задача по этому предложению
    existing = db.execute(
        select(CreatedTask).where(CreatedTask.suggestion_id == suggestion_id)
    ).scalar_one_or_none()
    if existing is not None:
        return {
            "already_created": True,
            "redmine_issue_id": existing.redmine_issue_id,
        }

    client = db.execute(
        select(Client).where(Client.id == suggestion.client_id)
    ).scalar_one_or_none()
    if client is None:
        raise ValueError(f"Клиент id={suggestion.client_id} не найден")

    # Создание задачи в Redmine
    issue_data = redmine_client.create_issue(
        project_id=client.redmine_project_id,
        subject=suggestion.title,
        description=(
            f"{suggestion.description or ''}\n\n"
            f"Обоснование: {suggestion.reason or ''}"
        ),
    )
    issue_id = issue_data["issue"]["id"]

    # Сохранение факта создания
    db.add(
        CreatedTask(
            suggestion_id=suggestion.id,
            client_id=client.id,
            redmine_project_id=client.redmine_project_id,
            redmine_issue_id=issue_id,
            title=suggestion.title,
        )
    )
    suggestion.status = "CREATED"
    db.commit()

    return {
        "already_created": False,
        "redmine_issue_id": issue_id,
    }