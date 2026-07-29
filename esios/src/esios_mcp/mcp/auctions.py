"""Specialized LLM-facing tools for e·sios auctions."""

from __future__ import annotations

from typing import Literal

from fastmcp import Context
from fastmcp.tools import ToolResult

from esios_mcp.api import ESIOS_API_BASE_URL, AuctionsApi, EsiosApiClient

from .common import run_api_call, validate_locale


async def esios_list_auctions(
    locale: Literal["es", "en"] = "es",
    year: int | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """List e·sios auctions, optionally filtered by a four-digit year."""
    locale = validate_locale(locale)
    if year is not None and (isinstance(year, bool) or year < 1000 or year > 9999):
        raise ValueError("year must be a four-digit year")
    request = {"locale": locale}
    if year is not None:
        request["year"] = year
    return await run_api_call(
        ctx=ctx,
        operation="Auction API list",
        url=f"{ESIOS_API_BASE_URL}/auctions",
        request=request,
        call=lambda: AuctionsApi(EsiosApiClient()).list(**request),
    )
