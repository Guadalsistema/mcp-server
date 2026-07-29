"""Specialized LLM-facing tools for e·sios indicators."""

from __future__ import annotations

from typing import Literal

from fastmcp import Context
from fastmcp.tools import ToolResult

from esios_mcp.api import ESIOS_API_BASE_URL, EsiosApiClient, IndicatorsApi

from .common import (
    run_api_call,
    validate_date_range,
    validate_indicator_id,
    validate_locale,
)


Locale = Literal["es", "en"]
TimeAggregation = Literal["sum", "average"]
TimeTruncation = Literal[
    "five_minutes",
    "ten_minutes",
    "fifteen_minutes",
    "hour",
    "day",
    "month",
    "year",
]
GeoAggregation = Literal["sum", "average"]
GeoTruncation = Literal[
    "country",
    "electric_system",
    "autonomous_community",
    "province",
    "electric_subsystem",
    "town",
    "drainage_basin",
]


async def esios_list_indicators(
    locale: Locale = "es",
    ctx: Context | None = None,
) -> str | ToolResult:
    """List available e·sios indicators, optionally translated to Spanish or English."""
    locale = validate_locale(locale)
    request = {"locale": locale}
    return await run_api_call(
        ctx=ctx,
        operation="Indicator API list",
        url=f"{ESIOS_API_BASE_URL}/indicators",
        request=request,
        call=lambda: IndicatorsApi(EsiosApiClient()).list(locale=locale),
    )


async def esios_search_indicators(
    text: str,
    locale: Locale = "es",
    ctx: Context | None = None,
) -> str | ToolResult:
    """Search e·sios indicators by name in the selected locale."""
    locale = validate_locale(locale)
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty search term")
    text = text.strip()
    request = {"locale": locale, "text": text}
    return await run_api_call(
        ctx=ctx,
        operation="Indicator API search",
        url=f"{ESIOS_API_BASE_URL}/indicators",
        request=request,
        call=lambda: IndicatorsApi(EsiosApiClient()).search(text, locale=locale),
    )


async def esios_get_indicator(
    indicator_id: int,
    locale: Locale = "es",
    datetime: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    time_agg: TimeAggregation = "sum",
    time_trunc: TimeTruncation | None = None,
    geo_agg: GeoAggregation = "sum",
    geo_ids: list[int] | None = None,
    geo_trunc: GeoTruncation | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """Retrieve one indicator and its values using an instant or date range.

    Use ``geo_ids`` to filter locations. When geographical grouping is needed,
    also provide ``geo_agg`` and ``geo_trunc`` according to the e·sios API.
    The returned ``data`` field preserves the upstream JSON payload.
    """
    indicator_id = validate_indicator_id(indicator_id)
    locale = validate_locale(locale)
    validate_date_range(start_date, end_date)
    if geo_ids is not None:
        if not geo_ids or any(isinstance(value, bool) or value <= 0 for value in geo_ids):
            raise ValueError("geo_ids must contain positive integers")

    request = {
        "indicator_id": indicator_id,
        "locale": locale,
        "datetime": datetime,
        "start_date": start_date,
        "end_date": end_date,
        "time_agg": time_agg,
        "time_trunc": time_trunc,
        "geo_agg": geo_agg,
        "geo_ids": geo_ids,
        "geo_trunc": geo_trunc,
    }
    request = {key: value for key, value in request.items() if value is not None}
    return await run_api_call(
        ctx=ctx,
        operation="Indicator API get",
        url=f"{ESIOS_API_BASE_URL}/indicators/{indicator_id}",
        request=request,
        call=lambda: IndicatorsApi(EsiosApiClient()).get(
            indicator_id,
            locale=locale,
            datetime=datetime,
            start_date=start_date,
            end_date=end_date,
            time_agg=time_agg,
            time_trunc=time_trunc,
            geo_agg=geo_agg,
            geo_ids=geo_ids,
            geo_trunc=geo_trunc,
        ),
    )
