from datetime import date
from sqlalchemy import select
from app.db import SessionLocal
from app.models.work_history import WorkHistory
from app.redmine.client import redmine_client

def main():
    db = SessionLocal()
    try:
        # Берем первую запись из Redmine
        entries = redmine_client.get_time_entries_all(from_date=date(2026,10,1), to_date=date(2026,10,31))
        entry = entries[0]
        hours_redmine = float(entry["hours"])
        
        # Ищем её в БД
        local = db.execute(
            select(WorkHistory).where(WorkHistory.redmine_time_entry_id == entry["id"])
        ).scalar_one_or_none()
        
        if local:
            print(f"Redmine: {hours_redmine} (тип: {type(hours_redmine)})")
            print(f"БД:      {local.hours} (тип: {type(local.hours)})")
            print(f"Разница: {float(local.hours) - hours_redmine}")
            print(f"Строка:  '{float(local.hours):.2f}' vs '{hours_redmine:.2f}'")
            print(f"Равны?   {f'{float(local.hours):.2f}' == f'{hours_redmine:.2f}'}")
        else:
            print("Запись не найдена в БД")
    finally:
        db.close()

if __name__ == "__main__":
    main()