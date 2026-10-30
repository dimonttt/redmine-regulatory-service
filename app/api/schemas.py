from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RunCreate(BaseModel):
    period_year: int
    period_month: int


class RunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    period_year: int
    period_month: int
    trigger_type: str
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    error_message: str | None = None


class SuggestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    source: str
    title: str
    description: str | None = None
    reason: str | None = None
    estimated_hours: float | None = None
    status: str
    created_at: datetime


class SuggestionStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str


class CreatedTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    suggestion_id: int
    client_id: int
    redmine_project_id: int
    redmine_issue_id: int
    title: str
    created_at: datetime