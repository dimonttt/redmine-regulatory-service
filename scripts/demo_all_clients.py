from datetime import date
from sqlalchemy import select, delete
from app.db import SessionLocal
from app.models.client import Client
from app.models.planned_hours import PlannedHours
from app.models.work_history import WorkHistory

def main():
    db = SessionLocal()
    try:
        print("1. Удаляем тестовые 150 часов у Клиента А...")
        # Находим клиента А
        client_a = db.execute(select(Client).where(Client.identifier == "klient-a")).scalar_one()
        
        # Удаляем все записи о времени у Клиента А, чтобы вернуть его к исходным 10 часам
        db.execute(delete(WorkHistory).where(WorkHistory.client_id == client_a.id))
        
        # Возвращаем ему исходные 3 задачи по 4, 3, 3 часа (чтобы было 10 часов)
        original_hours = [4.0, 3.0, 3.0]
        for i, hours in enumerate(original_hours):
            db.add(WorkHistory(
                client_id=client_a.id,
                regulatory_work_id=None,
                redmine_issue_id=i+1,
                redmine_time_entry_id=1000 + i, # Уникальный ID
                subject="Обновление сервера",
                hours=hours,
                spent_on=date(2026, 10, 9),
                activity="Разработка"
            ))
        
        print("2. Обновляем планы, чтобы у всех был недостаток...")
        # Устанавливаем план 50 часов для всех клиентов на Октябрь 2026
        plans = db.execute(
            select(PlannedHours).where(PlannedHours.period_year == 2026).where(PlannedHours.period_month == 10)
        ).scalars().all()
        
        for plan in plans:
            plan.planned_hours = 50.0
            
        db.commit()
        print("Готово! Теперь у Клиента А - 10 ч (план 50), у B - 45 ч (план 50), у C - 3 ч (план 50).")
        print("При следующем запуске расчета все трое будут проблемными!")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()