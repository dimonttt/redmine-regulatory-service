from datetime import date
from sqlalchemy import select, delete
from app.db import SessionLocal
from app.models.client import Client
from app.models.work_history import WorkHistory

def main():
    db = SessionLocal()
    try:
        print("Ищем Клиента А...")
        client_a = db.execute(select(Client).where(Client.identifier == "klient-a")).scalar_one_or_none()
        if not client_a:
            print("Клиент А не найден!")
            return

        print(f"Удаляем все текущие записи о времени для Клиента А (ID {client_a.id})...")
        # Удаляем все записи о трудозатратах для этого клиента
        db.execute(delete(WorkHistory).where(WorkHistory.client_id == client_a.id))
        
        print("Возвращаем исходные 10 часов (3 задачи по 4, 3, 3)...")
        # Добавляем обратно исходные записи
        original_hours = [4.0, 3.0, 3.0]
        for i, hours in enumerate(original_hours):
            db.add(WorkHistory(
                client_id=client_a.id,
                regulatory_work_id=None,
                redmine_issue_id=i+1,
                redmine_time_entry_id=1000 + i, # Уникальный ID, чтобы не было конфликтов
                subject="Обновление сервера",
                hours=hours,
                spent_on=date(2026, 10, 9),
                activity="Разработка"
            ))
        
        db.commit()
        print("Готово! Теперь у Клиента А снова 10 часов факта.")
        print("При следующем расчете он попадет в список проблемных!")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()