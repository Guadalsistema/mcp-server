"""Representations of the e·sios Widget V2 API endpoints."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .client import EsiosApiClient


class WidgetsApi:
    """Endpoint methods for listing and reading Widget V2 resources."""

    def __init__(self, client: EsiosApiClient) -> None:
        self.client = client

    def list(
        self,
        *,
        locale: str = "es",
        datetime: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        widget_type: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "locale": locale,
            "datetime": datetime,
            "start_date": start_date,
            "end_date": end_date,
            "widget_type": widget_type,
        }
        params = {key: value for key, value in params.items() if value is not None}
        return self.client.get("/widgets", params=params, api_version="v2")

    def get(
        self,
        widget_id_or_slug: int | str,
        *,
        locale: str = "es",
        datetime: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "locale": locale,
            "datetime": datetime,
            "start_date": start_date,
            "end_date": end_date,
        }
        params = {key: value for key, value in params.items() if value is not None}
        identifier = quote(str(widget_id_or_slug), safe="")
        return self.client.get(f"/widgets/{identifier}", params=params, api_version="v2")
