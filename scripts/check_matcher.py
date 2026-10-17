from app.db import SessionLocal
from app.services.calculation import calculate_client_hours
from app.services.matcher import select_works_for_client


def main():
    db = SessionLocal()
    try:
        results = calculate_client_hours(db, period_year=2026, period_month=10)
        for r in results:
            if not r["below_threshold"]:
                continue
            print(f"\n=== {r['client_name']} ===")
            print(f"План: {r['planned_hours']} ч, факт: {r['actual_hours']} ч, недостаток: {r['deficit_hours']} ч")
            works = select_works_for_client(
                db,
                client_id=r["client_id"],
                target_hours=r["deficit_hours"],
                period_year=2026,
                period_month=10,
            )
            total = 0.0
            for w in works:
                print(f"  - {w['name']} ({w['estimated_hours']} ч) [{w['category']}]")
                total += w["estimated_hours"]
            print(f"  Итого подобрано: {total} ч")
    finally:
        db.close()


if __name__ == "__main__":
    main()