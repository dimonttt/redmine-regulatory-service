from sqlalchemy import select

from app.db import SessionLocal
from app.models.client import Client
from app.models.planned_hours import PlannedHours


def main():
    db = SessionLocal()
    try:
        plans = [
            {"identifier": "klient-a", "planned": 40, "threshold": 5},
            {"identifier": "klient-b", "planned": 40, "threshold": 5},
            {"identifier": "klient-c", "planned": 40, "threshold": 5},
        ]

        for p in plans:
            client = db.execute(
                select(Client).where(Client.identifier == p["identifier"])
            ).scalar_one_or_none()
            if client is None:
                print(f"Клиент {p['identifier']} не найден")
                continue

            existing = db.execute(
                select(PlannedHours)
                .where(PlannedHours.client_id == client.id)
                .where(PlannedHours.period_year == 2026)
                .where(PlannedHours.period_month == 10)
            ).scalar_one_or_none()

            if existing is not None:
                print(f"План для {client.name} уже есть")
                continue

            db.add(
                PlannedHours(
                    client_id=client.id,
                    period_year=2026,
                    period_month=10,
                    planned_hours=p["planned"],
                    threshold_hours=p["threshold"],
                )
            )
            print(
                f"Создан план для {client.name}: "
                f"{p['planned']} ч, порог {p['threshold']} ч"
            )

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()