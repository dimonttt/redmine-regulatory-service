from app.db import SessionLocal
from app.services.calculation import calculate_client_hours


def main():
    db = SessionLocal()
    try:
        results = calculate_client_hours(db, period_year=2026, period_month=10)
        print(
            f"{'Клиент':<12} {'План':>6} {'Факт':>6} "
            f"{'Недостаток':>11} {'Порог':>6} {'Ниже порога':>12}"
        )
        print("-" * 60)
        for r in results:
            print(
                f"{r['client_name']:<12} "
                f"{r['planned_hours']:>6.2f} "
                f"{r['actual_hours']:>6.2f} "
                f"{r['deficit_hours']:>11.2f} "
                f"{r['threshold_hours']:>6.2f} "
                f"{'ДА' if r['below_threshold'] else 'нет':>12}"
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()