"""Specialized LLM-facing tools for Cached Widget V2."""

from __future__ import annotations

from typing import Literal

from fastmcp import Context
from fastmcp.tools import ToolResult

from esios_mcp.api import ESIOS_API_BASE_URL, CachedWidgetsApi, EsiosApiClient

from .common import run_api_call, validate_locale, validate_positive_id


async def esios_get_cached_widget_datetime(
    widget_id: int,
    locale: Literal["es", "en"] = "es",
    ctx: Context | None = None,
) -> str | ToolResult:
    """Retrieve the cache-key timestamp for a Widget V2 resource."""
    widget_id = validate_positive_id(widget_id, "widget_id")
    locale = validate_locale(locale)
    request = {"widget_id": widget_id, "locale": locale}
    return await run_api_call(
        ctx=ctx,
        operation="Cached Widget V2 API get",
        url=f"{ESIOS_API_BASE_URL}/cached_widgets/{widget_id}",
        request=request,
        call=lambda: CachedWidgetsApi(EsiosApiClient()).get(widget_id, locale=locale),
    )
