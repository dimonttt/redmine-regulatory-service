import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date

from app.db import SessionLocal
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