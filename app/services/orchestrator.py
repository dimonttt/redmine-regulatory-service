from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.calculation_run import CalculationRun
from app.models.suggestion import Suggestion
from app.services.calculation import calculate_client_hours
from app.services.llm_generation import generate_llm_suggestions
from app.services.matcher import select_works_for_client
from app.services.sync import sync_clients, sync_time_entries


def run_calculation(
    db: Session,
    period_year: int,
    period_month: int,
    trigger_type: str = "MANUAL",
) -> dict:
    #синхронизация - расчёт - подбор - LLM - сохранение предложений
    run = CalculationRun(
        period_year=period_year,
        period_month=period_month,
        trigger_type=trigger_type,
        status="RUNNING",
    ) 
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        # синхронизация
        sync_clients(db)
        if period_month == 12:
            period_end = date(period_year + 1, 1, 1)
        else:
            period_end = date(period_year, period_month + 1, 1)
        sync_time_entries(db, date(period_year, period_month, 1), period_end)

        # расчёт
        results = calculate_client_hours(db, period_year, period_month)
        problematic = [r for r in results if r["below_threshold"]]

        # подбор + LLM
        total_suggestions = 0
        for r in problematic:
            target = r["deficit_hours"]

            works = select_works_for_client(
                db,
                client_id=r["client_id"],
                target_hours=target,
                period_year=period_year,
                period_month=period_month,
            )
            covered = sum(w["estimated_hours"] for w in works)

            for w in works:
                db.add(
                    Suggestion(
                        calculation_run_id=run.id,
                        client_id=r["client_id"],
                        source="REGULATORY",
                        regulatory_work_id=w["id"],
                        title=w["name"],
                        description=w["description"],
                        reason=w["reason"],
                        estimated_hours=w["estimated_hours"],
                        status="NEW",
                    )
                )
                total_suggestions += 1

            remaining = target - covered
            if remaining > 0:
                try:
                    llm_suggestions = generate_llm_suggestions(
                        db,
                        client_id=r["client_id"],
                        target_hours=remaining,
                    )
                    for s in llm_suggestions:
                        db.add(
                            Suggestion(
                                calculation_run_id=run.id,
                                client_id=r["client_id"],
                                source="LLM",
                                regulatory_work_id=None,
                                title=s["title"],
                                description=s["description"],
                                reason=s["reason"],
                                estimated_hours=s["estimated_hours"],
                                status="NEW",
                            )
                        )
                        total_suggestions += 1
                except Exception as e:
                    print(f"LLM failed for {r['client_name']}: {e}")

        # завершение
        run.status = "COMPLETED"
        run.finished_at = datetime.utcnow()
        db.commit()

        return {
            "run_id": run.id,
            "status": "COMPLETED",
            "period": f"{period_year}-{period_month:02d}",
            "clients_total": len(results),
            "clients_problematic": len(problematic),
            "suggestions_created": total_suggestions,
        }

    except Exception as e:
        run.status = "FAILED"
        run.finished_at = datetime.utcnow()
        run.error_message = str(e)
        db.commit()
        raise