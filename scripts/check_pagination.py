from datetime import date
from app.redmine.client import redmine_client

def main():
    from_date = date(2026, 10, 1)
    to_date = date(2026, 10, 31)
    
    print("СТАРЫЙ МЕТОД (без пагинации) ")
    old_data = redmine_client.get_time_entries(from_date=from_date, to_date=to_date)
    print(f"Получено записей: {len(old_data['time_entries'])}")
    print(f"Всего на сервере: {old_data['total_count']}")
    
    print("\nНОВЫЙ МЕТОД")
    new_data = redmine_client.get_time_entries_all(from_date=from_date, to_date=to_date)
    print(f"Получено записей: {len(new_data)}")

if __name__ == "__main__":
    main()