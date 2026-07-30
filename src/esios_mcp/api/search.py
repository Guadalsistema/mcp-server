"""Representations of e·sios search endpoints."""

from __future__ import annotations

from typing import Any

from .client import EsiosApiClient


class SearchApi:
    """Endpoint methods for content-only and combined searches."""

    def __init__(self, client: EsiosApiClient) -> None:
        self.client = client

    def contents(self, query: str, *, locale: str = "es") -> dict[str, Any]:
        return self.client.get("/contents", params={"locale": locale, "query": query})

    def contents_and_indicators(self, query: str, *, locale: str = "es") -> dict[str, Any]:
        return self.client.get("/search", params={"locale": locale, "query": query})
