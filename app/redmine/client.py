from datetime import date
from typing import Any

import httpx

from app.config import settings


class RedmineClient:
    """HTTP-клиент для Redmine API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
    ):
        self.base_url = (base_url or settings.redmine_url).rstrip("/")
        self.api_key = api_key or settings.redmine_api_key
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "X-Redmine-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=self.timeout, trust_env=False) as client:
            response = client.get(url, headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json()

    def get_projects(self, limit: int = 100, offset: int = 0) -> dict:
        """Получить список проектов."""
        return self._get("/projects.json", {"limit": limit, "offset": offset})

    def get_issues(
        self,
        project_id: int | None = None,
        status_id: str = "*",
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """Получить список задач, при необходимости — по конкретному проекту."""
        params: dict[str, Any] = {
            "status_id": status_id,
            "limit": limit,
            "offset": offset,
        }
        if project_id is not None:
            params["project_id"] = project_id
        return self._get("/issues.json", params)

    def get_time_entries(
        self,
        project_id: int | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """Получить записи о трудозатратах за период."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if project_id is not None:
            params["project_id"] = project_id
        if from_date is not None:
            params["from"] = from_date.isoformat()
        if to_date is not None:
            params["to"] = to_date.isoformat()
        return self._get("/time_entries.json", params)


redmine_client = RedmineClient()