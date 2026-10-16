from datetime import date

from app.db import SessionLocal
from app.services.sync import sync_clients, sync_time_entries


def main():
    db = SessionLocal()
    try:
        print("Синхронизация клиентов...")
        result = sync_clients(db)
        print(f"  Создано: {result['created']}, обновлено: {result['updated']}")

        print("Синхронизация трудозатрат за октябрь 2026...")
        result = sync_time_entries(db, date(2026, 10, 1), date(2026, 10, 31))
        print(f"  Создано: {result['created']}, пропущено: {result['skipped']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()