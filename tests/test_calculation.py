from datetime import date
from app.models.work_history import WorkHistory
from app.models.monthly_aggregate import MonthlyAggregate
from app.services.calculation import calculate_client_hours

def _add_aggregate(db, client_id, hours):
    agg = MonthlyAggregate(
        id=1, 
        client_id=client_id,
        period_year=2026,
        period_month=10,
        total_hours=hours
    )
    db.add(agg)
    db.commit()

def test_below_threshold(db, sample_client, sample_plan):
    # Клиент отработал 10 часов при плане 40 - недостаток 30, ниже порога
    _add_aggregate(db, sample_client.id, 10.0)
    
    results = calculate_client_hours(db, 2026, 10)
    
    assert len(results) == 1
    r = results[0]
    assert r["actual_hours"] == 10.0

def test_within_threshold(db, sample_client, sample_plan):
    # Клиент отработал 37 часов при плане 40 - недостаток 3 (меньше порога 5)
    _add_aggregate(db, sample_client.id, 37.0)
    results = calculate_client_hours(db, 2026, 10)
    
    r = results[0]
    assert r["actual_hours"] == 37.0
    assert r["deficit_hours"] == 3.0
    assert r["below_threshold"] is False

def test_no_data_for_client(db, sample_client, sample_plan):
    # Если данных нет, сервис должен вернуть 0 часов
    results = calculate_client_hours(db, 2026, 10)
    
    r = results[0]
    assert r["actual_hours"] == 0.0
    assert r["deficit_hours"] == 40.0
    assert r["below_threshold"] is True