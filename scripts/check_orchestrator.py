from app.db import SessionLocal
from app.services.orchestrator import run_calculation


def main():
    db = SessionLocal()
    try:
        print("Запуск полного расчета за октябрь 2026...")
        result = run_calculation(db, period_year=2026, period_month=10)
        print("\nРезультат:")
        for k, v in result.items():
            print(f"  {k}: {v}")
    finally:
        db.close()


if __name__ == "__main__":
    main()