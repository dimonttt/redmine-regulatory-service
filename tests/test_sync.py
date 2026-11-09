from datetime import date
from unittest.mock import patch
from app.models.work_history import WorkHistory
from app.services.sync import sync_time_entries

@patch("app.services.sync.redmine_client.get_time_entries_all")
def test_sync_skips_existing_entries(mock_get_entries, db, sample_client):
    # Добавляем запись вручную с явным ID
    db.add(WorkHistory(
        id=1, # <--- Явный ID
        client_id=sample_client.id,
        redmine_issue_id=1,
        redmine_time_entry_id=1,
        hours=5.0,
        spent_on=date(2026, 10, 9),
        activity="Разработка"
    ))
    db.commit()
    
    mock_get_entries.return_value = [
        {
            "id": 1,
            "project": {"id": sample_client.redmine_project_id},
            "issue": {"id": 1},
            "hours": 5.0,
            "spent_on": date(2026, 10, 9),
            "activity": {"name": "Разработка"}
        }
    ]
    
    result = sync_time_entries(db, date(2026, 10, 1), date(2026, 10, 31))
    
    assert result["created"] == 0
    assert result["skipped"] == 1