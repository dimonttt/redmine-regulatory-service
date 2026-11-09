import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models.client import Client
from app.models.planned_hours import PlannedHours
from app.models.work_history import WorkHistory
from app.models.monthly_aggregate import MonthlyAggregate


@pytest.fixture(scope="function")
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[
        Client.__table__,
        PlannedHours.__table__,
        WorkHistory.__table__,
        MonthlyAggregate.__table__,
    ])
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_client(db):
    client = Client(
        id=1,
        redmine_project_id=999,
        name="Тестовый клиент",
        identifier="test-client",
        is_active=True,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@pytest.fixture
def sample_plan(db, sample_client):
    plan = PlannedHours(
        id=1,
        client_id=sample_client.id,
        period_year=2026,
        period_month=10,
        planned_hours=40,
        threshold_hours=5,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan