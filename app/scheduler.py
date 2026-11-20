import logging
from sqlalchemy import select
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date

from app.db import SessionLocal
from app.models.suggestion import Suggestion
from app.services.calculation import calculate_client_hours
from app.services.email_sender import send_report_email
from app.services.orchestrator import run_calculation

logger = logging.getLogger(__name__)

def scheduled_run():
    db = SessionLocal()
    try:
        today = date.today()
        if today.month == 1:
            year, month = today.year - 1, 12
        else:
            year, month = today.year, today.month - 1

        logger.info(f"Запуск расчета по расписанию за {year}-{month}")
        result = run_calculation(db, period_year=year, period_month=month, trigger_type="SCHEDULED")
        logger.info(f"Расчет завершен: {result}")

        calc_results = calculate_client_hours(db, year, month)
        clients_data = []
        for r in calc_results:
            suggestions = db.execute(
                select(Suggestion)
                .where(Suggestion.calculation_run_id == result["run_id"])
                .where(Suggestion.client_id == r["client_id"])
            ).scalars().all()

            clients_data.append({
                "name": r["client_name"],
                "planned_hours": r["planned_hours"],
                "actual_hours": r["actual_hours"],
                "deficit_hours": r["deficit_hours"],
                "below_threshold": r["below_threshold"],
                "suggestions": [{"title": s.title, "estimated_hours": s.estimated_hours, "reason": s.reason}
                                for s in suggestions
                ],
            })

            send_report_email(year, month, clients_data)
    except Exception as e:
        logger.error(f"Ошибка при запуске расчета по расписанию: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_run, 'cron', day=1, hour=3, minute=0)
    scheduler.start()
    print("ПЛАНИРОВЩИК ЗАПУЩЕН: 1-е число каждого месяца в 03:00")
    return scheduler