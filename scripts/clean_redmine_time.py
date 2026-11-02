import httpx
from app.redmine.client import redmine_client

def main():
    print("Ищем все записи с комментарием 'Тестовая запись'...")
    
    # Получаем все записи за октябрь
    entries = redmine_client.get_time_entries_all()
    
    deleted = 0
    with httpx.Client(trust_env=False) as client:
        for entry in entries:
            comments = entry.get("comments", "")
            # Если это наша тестовая запись
            if "Тестовая запись" in comments:
                url = f"{redmine_client.base_url}/time_entries/{entry['id']}.json"
                r = client.delete(url, headers=redmine_client._headers())
                if r.status_code == 204:
                    deleted += 1
                    
    print(f"Удалено из Redmine: {deleted} записей.")
    print("Теперь запусти синхронизацию и расчет заново!")

if __name__ == "__main__":
    main()