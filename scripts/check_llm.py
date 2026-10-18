import json

from app.db import SessionLocal
from app.services.calculation import calculate_client_hours
from app.services.llm_generation import generate_llm_suggestions


def main():
    db = SessionLocal()
    try:
        results = calculate_client_hours(db, period_year=2026, period_month=10)
        for r in results:
            if not r["below_threshold"]:
                continue
            print(f"\n=== {r['client_name']} ===")
            print(f"Недостаток: {r['deficit_hours']} ч")
            print("Запрос к LLM...")

            try:
                suggestions = generate_llm_suggestions(
                    db,
                    client_id=r["client_id"],
                    target_hours=r["deficit_hours"],
                )
            except Exception as e:
                print(f"ОШИБКА: {e}")
                continue

            for s in suggestions:
                print(f"  - {s['title']} ({s['estimated_hours']} ч)")
                print(f"    Описание: {s['description']}")
                print(f"    Обоснование: {s['reason']}")
                print()
    finally:
        db.close()


if __name__ == "__main__":
    main()