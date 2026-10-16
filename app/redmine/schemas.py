from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class RedmineProject(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    identifier: str | None = None
    status: int = 1


class RedmineProjectsResponse(BaseModel):
    projects: list[RedmineProject]
    total_count: int
    offset: int = 0
    limit: int = 25


class RedmineTimeEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    project: dict
    issue: dict | None = None
    user: dict | None = None
    activity: dict | None = None
    hours: float
    comments: str | None = ""
    spent_on: date


class RedmineTimeEntriesResponse(BaseModel):
    time_entries: list[RedmineTimeEntry]
    total_count: int
    offset: int = 0
    limit: int = 25


class RedmineIssue(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    project: dict
    subject: str
    description: str | None = ""
    status: dict | None = None
    tracker: dict | None = None
    created_on: datetime | None = None
    updated_on: datetime | None = None


class RedmineIssuesResponse(BaseModel):
    issues: list[RedmineIssue]
    total_count: int
    offset: int = 0
    limit: int = 25