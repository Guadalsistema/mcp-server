"""Specialized LLM-facing tools for e·sios offers."""

from __future__ import annotations

from typing import Literal

from fastmcp import Context
from fastmcp.tools import ToolResult

from esios_mcp.api import ESIOS_API_BASE_URL, EsiosApiClient, OfferIndicatorsApi, OfferWidgetsApi

from .common import (
    run_api_call,
    validate_date_range,
    validate_indicator_id,
    validate_locale,
    validate_widget_identifier,
)


async def esios_get_offer_widget(
    widget_id_or_slug: int | str,
    locale: Literal["es", "en"] = "es",
    datetime: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """Retrieve an Offer Widget V2 resource by ID or slug."""
    identifier = validate_widget_identifier(widget_id_or_slug)
    locale = validate_locale(locale)
    validate_date_range(start_date, end_date)
    request = {
        "widget_id_or_slug": identifier,
        "locale": locale,
        "datetime": datetime,
        "start_date": start_date,
        "end_date": end_date,
    }
    request = {key: value for key, value in request.items() if value is not None}
    return await run_api_call(
        ctx=ctx,
        operation="Offer Widget V2 API get",
        url=f"{ESIOS_API_BASE_URL}/widgets/{identifier}",
        request=request,
        call=lambda: OfferWidgetsApi(EsiosApiClient()).get(
            identifier,
            locale=locale,
            datetime=datetime,
            start_date=start_date,
            end_date=end_date,
        ),
    )


async def esios_get_offer_indicator(
    indicator_id: int,
    locale: Literal["es", "en"] = "es",
    datetime: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """Retrieve an OfferIndicator by ID for an instant or date range."""
    indicator_id = validate_indicator_id(indicator_id)
    locale = validate_locale(locale)
    validate_date_range(start_date, end_date)
    request = {
        "indicator_id": indicator_id,
        "locale": locale,
        "datetime": datetime,
        "start_date": start_date,
        "end_date": end_date,
    }
    request = {key: value for key, value in request.items() if value is not None}
    return await run_api_call(
        ctx=ctx,
        operation="OfferIndicator API get",
        url=f"{ESIOS_API_BASE_URL}/offer_indicators/{indicator_id}",
        request=request,
        call=lambda: OfferIndicatorsApi(EsiosApiClient()).get(
            indicator_id,
            locale=locale,
            datetime=datetime,
            start_date=start_date,
            end_date=end_date,
        ),
    )
