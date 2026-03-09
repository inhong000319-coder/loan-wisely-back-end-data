from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class NotionApiError(RuntimeError):
    def __init__(self, status_code: int, body: str):
        super().__init__(f"Notion API error ({status_code}): {body}")
        self.status_code = status_code
        self.body = body


class NotionClient:
    def __init__(self, token: str, api_version: str = "2022-06-28") -> None:
        if not token:
            raise ValueError("Notion token is required")
        self.token = token
        self.api_version = api_version
        self.base_url = "https://api.notion.com/v1"

    @classmethod
    def from_env(cls) -> "NotionClient":
        token = os.getenv("NOTION_TOKEN", "").strip()
        version = os.getenv("NOTION_API_VERSION", "2022-06-28").strip() or "2022-06-28"
        return cls(token=token, api_version=version)

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        body = None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": self.api_version,
            "Content-Type": "application/json",
        }
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            raise NotionApiError(e.code, error_body) from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Notion API request failed: {e}") from e

    def create_page(
        self,
        parent_page_id: str,
        title: str,
        children: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "properties": {
                "title": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": title},
                        }
                    ]
                }
            },
        }
        if children:
            payload["children"] = children
        return self._request("POST", "/pages", payload)

    def create_database(
        self,
        parent_page_id: str,
        title: str,
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        payload = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": [
                {
                    "type": "text",
                    "text": {"content": title},
                }
            ],
            "properties": properties,
        }
        return self._request("POST", "/databases", payload)

    def retrieve_database(self, database_id: str) -> dict[str, Any]:
        return self._request("GET", f"/databases/{database_id}")

    def update_database(self, database_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self._request("PATCH", f"/databases/{database_id}", {"properties": properties})

    def append_block_children(self, block_id: str, children: list[dict[str, Any]]) -> dict[str, Any]:
        return self._request("PATCH", f"/blocks/{block_id}/children", {"children": children})

    def create_database_page(
        self,
        database_id: str,
        properties: dict[str, Any],
        children: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "parent": {"database_id": database_id},
            "properties": properties,
        }
        if children:
            payload["children"] = children
        return self._request("POST", "/pages", payload)

    def query_database(self, database_id: str, query: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("POST", f"/databases/{database_id}/query", query or {})

    def update_page_properties(self, page_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self._request("PATCH", f"/pages/{page_id}", {"properties": properties})


def load_json_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
