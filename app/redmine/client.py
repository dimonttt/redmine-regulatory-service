from datetime import date
from typing import Any

import httpx

from app.config import settings

class RedmineClient:
    # HTTP-клиент для Redmine API
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

    def _get_all_pages(self, path: str, base_params: dict | None = None) -> list:
        # сбор всех записей из Redmine
        all_items = []
        offset = 0
        limit = 100
        
        while True:
            params = dict(base_params or {})
            params["limit"] = limit
            params["offset"] = offset
            
            data = self._get(path, params)
            
            # Определяем ключ, под которым лежат данные (зависит от endpoint)
            # Но мы можем просто взять первый попавшийся список в словаре, кроме служебных полей
            items = next((v for k, v in data.items() if isinstance(v, list)), [])
            all_items.extend(items)
            
            # Смотрим, сколько всего записей на сервере
            total = data.get("total_count", 0)
            
            # Если мы собрали всё, или сервер вернул пустоту - выходим из цикла
            if offset + len(items) >= total or not items:
                break
            
            offset += limit
            
        return all_items

    def get_projects(self, limit: int = 100, offset: int = 0) -> dict:
        # получить список проектов
        return self._get("/projects.json", {"limit": limit, "offset": offset})

    def get_issues(
        self,
        project_id: int | None = None,
        status_id: str = "*",
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
       # Получить список задач, при необходимости — по конкретному проекту
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
        # получить трудозатратах
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if project_id is not None:
            params["project_id"] = project_id
        if from_date is not None:
            params["from"] = from_date.isoformat()
        if to_date is not None:
            params["to"] = to_date.isoformat()
        return self._get("/time_entries.json", params)


    def get_projects_all(self) -> list:
        """Возвращает ВСЕ проекты."""
        return self._get_all_pages("/projects.json")

    def get_time_entries_all(self, from_date=None, to_date=None) -> list:
        """Возвращает ВСЕ трудозатраты за период."""
        params = {}
        if from_date:
            params["from"] = from_date.isoformat()
        if to_date:
            params["to"] = to_date.isoformat()
        return self._get_all_pages("/time_entries.json", params)

    def get_issues_all(
        self,
        project_id: int | None = None,
        status_id: str = "*",
    ) -> list[dict]:
        """Получает ВСЕ задачи, автоматически проходя по страницам."""
        params: dict[str, Any] = {"status_id": status_id}
        if project_id is not None:
            params["project_id"] = project_id
            
        return self._get_all_pages("/issues.json", params)

    def create_issue(
        self,
        project_id: int,
        subject: str,
        description: str = "",
        tracker_id: int = 1,
        status_id: int = 1,
    ) -> dict:
        # Создаёт задачу в Redmine. Возвращает созданный объект issue
        payload = {
            "issue": {
                "project_id": project_id,
                "subject": subject,
                "description": description,
                "tracker_id": tracker_id,
                "status_id": status_id,
            }
        }
        url = f"{self.base_url}/issues.json"
        with httpx.Client(timeout=self.timeout, trust_env=False) as client:
            response = client.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()


redmine_client = RedmineClient()