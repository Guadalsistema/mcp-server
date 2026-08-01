"""Representation of the e·sios Auction API."""

from __future__ import annotations

from typing import Any

from .client import EsiosApiClient


class AuctionsApi:
    """Endpoint methods for listing auctions."""

    def __init__(self, client: EsiosApiClient) -> None:
        self.client = client

    def list(self, *, locale: str = "es", year: int | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"locale": locale}
        if year is not None:
            params["year"] = year
        return self.client.get("/auctions", params=params)
