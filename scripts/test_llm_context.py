from app.db import SessionLocal
from app.services.llm_generation import generate_llm_suggestions
from app.models.client import Client
from sqlalchemy import select

def main():
    db = SessionLocal()
    try:
        client = db.execute(
            select(Client).where(Client.identifier == "klient-c")
        ).scalar_one_or_none()
        
        if not client:
            print("Клиент не найден")
            return

        print(f"Запрос к LLM для клиента: {client.name}")
        print(f"Отрасль: {client.industry}")
        print(f"Описание: {client.description}")
        print("Ждем ответа...")

        # запрашиваем работы на 10 часов
        suggestions = generate_llm_suggestions(db, client_id=client.id, target_hours=10)
        
        print("\n--- Предложения от LLM ---")
        for s in suggestions:
            print(f"\nНазвание: {s['title']}")
            print(f"Часы: {s['estimated_hours']}")
            print(f"Обоснование: {s['reason']}")
            
    finally:
        db.close()

if __name__ == "__main__":
    main()