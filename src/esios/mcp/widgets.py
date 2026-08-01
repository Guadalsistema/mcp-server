"""Specialized LLM-facing tools for e·sios Widget V2 resources."""

from __future__ import annotations

from typing import Literal

from fastmcp import Context
from fastmcp.tools import ToolResult

from esios.api import ESIOS_API_BASE_URL, EsiosApiClient, WidgetsApi

from .common import (
    run_api_call,
    validate_date_range,
    validate_locale,
    validate_widget_identifier,
)


Locale = Literal["es", "en"]
WidgetType = Literal["offer", "widget"]


async def esios_list_widgets(
    locale: Locale = "es",
    datetime: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    widget_type: WidgetType | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """List e·sios Widget V2 resources, optionally filtered by type or time."""
    locale = validate_locale(locale)
    validate_date_range(start_date, end_date)
    request = {
        "locale": locale,
        "datetime": datetime,
        "start_date": start_date,
        "end_date": end_date,
        "widget_type": widget_type,
    }
    request = {key: value for key, value in request.items() if value is not None}
    return await run_api_call(
        ctx=ctx,
        operation="Widget V2 API list",
        url=f"{ESIOS_API_BASE_URL}/widgets",
        request=request,
        call=lambda: WidgetsApi(EsiosApiClient()).list(
            locale=locale,
            datetime=datetime,
            start_date=start_date,
            end_date=end_date,
            widget_type=widget_type,
        ),
    )


async def esios_get_widget(
    widget_id_or_slug: int | str,
    locale: Locale = "es",
    datetime: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """Retrieve one e·sios Widget V2 resource by numeric ID or slug."""
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
        operation="Widget V2 API get",
        url=f"{ESIOS_API_BASE_URL}/widgets/{identifier}",
        request=request,
        call=lambda: WidgetsApi(EsiosApiClient()).get(
            identifier,
            locale=locale,
            datetime=datetime,
            start_date=start_date,
            end_date=end_date,
        ),
    )
