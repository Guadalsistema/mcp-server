"""Specialized LLM-facing tools for e·sios search."""

from __future__ import annotations

from typing import Literal

from fastmcp import Context
from fastmcp.tools import ToolResult

from esios.api import ESIOS_API_BASE_URL, EsiosApiClient, SearchApi

from .common import run_api_call, validate_locale, validate_nonempty


async def esios_search_contents(
    query: str,
    locale: Literal["es", "en"] = "es",
    ctx: Context | None = None,
) -> str | ToolResult:
    """Search content records by text."""
    query = validate_nonempty(query, "query")
    locale = validate_locale(locale)
    request = {"query": query, "locale": locale}
    return await run_api_call(
        ctx=ctx,
        operation="Content search API",
        url=f"{ESIOS_API_BASE_URL}/contents",
        request=request,
        call=lambda: SearchApi(EsiosApiClient()).contents(query, locale=locale),
    )


async def esios_search_contents_and_indicators(
    query: str,
    locale: Literal["es", "en"] = "es",
    ctx: Context | None = None,
) -> str | ToolResult:
    """Search across content and indicator records by text."""
    query = validate_nonempty(query, "query")
    locale = validate_locale(locale)
    request = {"query": query, "locale": locale}
    return await run_api_call(
        ctx=ctx,
        operation="Content and indicator search API",
        url=f"{ESIOS_API_BASE_URL}/search",
        request=request,
        call=lambda: SearchApi(EsiosApiClient()).contents_and_indicators(query, locale=locale),
    )
