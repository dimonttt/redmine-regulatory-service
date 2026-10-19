from app.db import SessionLocal
from app.services.task_creator import create_task_from_suggestion


def main():
    db = SessionLocal()
    try:
        suggestion_id = 1  # ← подставь свой id из шага 3

        print(f"Создание задачи из предложения id={suggestion_id}...")
        result = create_task_from_suggestion(db, suggestion_id)
        if result["already_created"]:
            print(f"Задача уже была создана ранее: issue_id={result['redmine_issue_id']}")
        else:
            print(f"Создана задача в Redmine: issue_id={result['redmine_issue_id']}")

        print("\nПовторный запуск (проверка защиты от дублей)...")
        result = create_task_from_suggestion(db, suggestion_id)
        if result["already_created"]:
            print(f"Дубль не создан, используется существующий: issue_id={result['redmine_issue_id']}")
        else:
            print(f"ОШИБКА: создан дубль!")
    finally:
        db.close()


if __name__ == "__main__":
    main()