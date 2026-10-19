from sqlalchemy import select

from app.db import SessionLocal
from app.models.calculation_run import CalculationRun
from app.models.client import Client
from app.models.suggestion import Suggestion


def main():
    db = SessionLocal()
    try:
        # Создаём запуск расчёта
        run = CalculationRun(
            period_year=2026,
            period_month=10,
            trigger_type="MANUAL",
            status="COMPLETED",
        )
        db.add(run)
        db.flush()  # чтобы получить run.id

        # Берём Клиента А
        client = db.execute(
            select(Client).where(Client.identifier == "klient-a")
        ).scalar_one_or_none()
        if client is None:
            print("Клиент А не найден")
            return

        # Создаём предложение
        suggestion = Suggestion(
            calculation_run_id=run.id,
            client_id=client.id,
            source="REGULATORY",
            title="Настройка мониторинга",
            description="Развёртывание и настройка агентов мониторинга",
            reason="Восполнение недостатка часов по клиенту",
            estimated_hours=6,
            status="APPROVED",
        )
        db.add(suggestion)
        db.commit()

        print(f"Создано предложение id={suggestion.id} для клиента {client.name}")
        print(f"Run id={run.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()