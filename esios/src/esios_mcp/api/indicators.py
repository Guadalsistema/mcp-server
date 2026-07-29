"""Representations of the e·sios Indicator API endpoints."""

from __future__ import annotations

from typing import Any

from .client import EsiosApiClient


class IndicatorsApi:
    """Endpoint methods for listing, searching, and reading indicators."""

    def __init__(self, client: EsiosApiClient) -> None:
        self.client = client

    def list(self, *, locale: str = "es") -> dict[str, Any]:
        return self.client.get("/indicators", params={"locale": locale}, api_version="v1")

    def search(self, text: str, *, locale: str = "es") -> dict[str, Any]:
        return self.client.get(
            "/indicators",
            params={"locale": locale, "text": text},
            api_version="v1",
        )

    def get(
        self,
        indicator_id: int,
        *,
        locale: str = "es",
        datetime: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        time_agg: str = "sum",
        time_trunc: str | None = None,
        geo_agg: str = "sum",
        geo_ids: list[int] | None = None,
        geo_trunc: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "locale": locale,
            "datetime": datetime,
            "start_date": start_date,
            "end_date": end_date,
            "time_agg": time_agg,
            "time_trunc": time_trunc,
            "geo_agg": geo_agg,
            "geo_trunc": geo_trunc,
        }
        params = {key: value for key, value in params.items() if value is not None}
        if geo_ids:
            params["geo_ids[]"] = [str(geo_id) for geo_id in geo_ids]
        return self.client.get(f"/indicators/{indicator_id}", params=params, api_version="v1")
