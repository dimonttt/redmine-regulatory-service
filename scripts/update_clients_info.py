from sqlalchemy import select
from app.db import SessionLocal
from app.models.client import Client

def main():
    db = SessionLocal()
    try:
        data = {
            "klient-a": {"desc": "Крупный банк. Система онлайн-платежей и процессинг карт.", "ind": "Финтех"},
            "klient-b": {"desc": "Сеть розничных магазинов. Учет товаров и кассовое ПО.", "ind": "Ритейл"},
            "klient-c": {"desc": "Медицинская лаборатория. Обработка результатов анализов.", "ind": "Медицина"},
        }

        for identifier, info in data.items():
            client = db.execute(select(Client).where(Client.identifier == identifier)).scalar_one_or_none()
            if client:
                client.description = info["desc"]
                client.industry = info["ind"]
        
        db.commit()
        print("Информация о клиентах обновлена")
    finally:
        db.close()

if __name__ == "__main__":
    main()