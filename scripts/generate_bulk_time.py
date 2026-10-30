from datetime import date
from app.redmine.client import redmine_client

def main():
    print("Генерация 150 записей о трудозатратах в Redmine...")
    # Берем проект Клиент А (id=1) и задачу (id=1)
    project_id = 1
    issue_id = 1
    activity_id = 5
    
    for i in range(150):
        # Создаем запись напрямую через API Redmine
        url = f"{redmine_client.base_url}/time_entries.json"
        payload = {
            "time_entry": {
                "issue_id": issue_id,
                "hours": 1,
                "spent_on": "2026-10-15",
                "activity_id": activity_id,
                "comments": f"Тестовая запись {i+1}"
            }
        }
        import httpx
        with httpx.Client(trust_env=False) as client:
            r = client.post(url, headers=redmine_client._headers(), json=payload)
            r.raise_for_status()
    
    print("Готово! Создано 150 записей.")

if __name__ == "__main__":
    main()