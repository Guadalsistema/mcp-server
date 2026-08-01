"""Representation of the Cached Widget V2 endpoint."""

from __future__ import annotations

from typing import Any

from .client import EsiosApiClient


class CachedWidgetsApi:
    """Endpoint methods for Widget V2 cache-key timestamps."""

    def __init__(self, client: EsiosApiClient) -> None:
        self.client = client

    def get(self, widget_id: int, *, locale: str = "es") -> dict[str, Any]:
        return self.client.get(
            f"/cached_widgets/{widget_id}",
            params={"locale": locale},
            api_version="v2",
        )
