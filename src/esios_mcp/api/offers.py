"""Representations of e·sios Offer Widget and OfferIndicator endpoints."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .client import EsiosApiClient


def _time_params(
    *,
    locale: str,
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
    return {key: value for key, value in params.items() if value is not None}


class OfferWidgetsApi:
    """Endpoint methods for Offer Widget V2 resources."""

    def __init__(self, client: EsiosApiClient) -> None:
        self.client = client

    def get(
        self,
        widget_id_or_slug: int | str,
        *,
        locale: str = "es",
        datetime: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        identifier = quote(str(widget_id_or_slug), safe="")
        return self.client.get(
            f"/widgets/{identifier}",
            params=_time_params(
                locale=locale,
                datetime=datetime,
                start_date=start_date,
                end_date=end_date,
            ),
            api_version="v2",
        )


class OfferIndicatorsApi:
    """Endpoint methods for OfferIndicator resources."""

    def __init__(self, client: EsiosApiClient) -> None:
        self.client = client

    def get(
        self,
        indicator_id: int,
        *,
        locale: str = "es",
        datetime: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        return self.client.get(
            f"/offer_indicators/{indicator_id}",
            params=_time_params(
                locale=locale,
                datetime=datetime,
                start_date=start_date,
                end_date=end_date,
            ),
        )
