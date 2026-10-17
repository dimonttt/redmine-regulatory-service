from sqlalchemy import select

from app.db import SessionLocal
from app.models.regulatory_work import RegulatoryWork


WORKS = [
    {
        "code": "BACKUP_CHECK",
        "name": "Проверка резервных копий",
        "description": "Проверка актуальности резервных копий и тестовое восстановление",
        "category": "Бэкапы",
        "estimated_hours": 2,
    },
    {
        "code": "SECURITY_UPDATE",
        "name": "Обновление безопасности сервера",
        "description": "Установка патчей безопасности ОС и сервисов",
        "category": "Безопасность",
        "estimated_hours": 4,
    },
    {
        "code": "LOG_AUDIT",
        "name": "Аудит журналов",
        "description": "Анализ журналов на предмет ошибок и подозрительной активности",
        "category": "Мониторинг",
        "estimated_hours": 3,
    },
    {
        "code": "DISK_CLEANUP",
        "name": "Очистка дискового пространства",
        "description": "Удаление временных файлов и старых логов",
        "category": "Обслуживание",
        "estimated_hours": 1,
    },
    {
        "code": "DB_OPTIMIZE",
        "name": "Оптимизация базы данных",
        "description": "Анализ медленных запросов, обновление статистики",
        "category": "Базы данных",
        "estimated_hours": 5,
    },
    {
        "code": "MONITORING_SETUP",
        "name": "Настройка мониторинга",
        "description": "Развёртывание и настройка агентов мониторинга",
        "category": "Мониторинг",
        "estimated_hours": 6,
    },
    {
        "code": "SSL_RENEW",
        "name": "Обновление SSL-сертификатов",
        "description": "Проверка сроков и обновление сертификатов",
        "category": "Безопасность",
        "estimated_hours": 2,
    },
    {
        "code": "DOCKER_HARDENING",
        "name": "Упрочнение Docker-окружения",
        "description": "Аудит конфигураций контейнеров, ограничение прав",
        "category": "Контейнеры",
        "estimated_hours": 4,
    },
    {
        "code": "PERF_REVIEW",
        "name": "Обзор производительности",
        "description": "Снятие метрик нагрузки, рекомендации по оптимизации",
        "category": "Производительность",
        "estimated_hours": 5,
    },
    {
        "code": "DOC_UPDATE",
        "name": "Актуализация документации",
        "description": "Обновление технической документации по инфраструктуре",
        "category": "Документация",
        "estimated_hours": 3,
    },
]


def main():
    db = SessionLocal()
    try:
        created = 0
        skipped = 0
        for w in WORKS:
            existing = db.execute(
                select(RegulatoryWork).where(RegulatoryWork.code == w["code"])
            ).scalar_one_or_none()
            if existing is not None:
                skipped += 1
                continue
            db.add(RegulatoryWork(**w, is_active=True))
            created += 1
        db.commit()
        print(f"Создано: {created}, пропущено: {skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    main()