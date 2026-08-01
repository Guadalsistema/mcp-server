"""Structured FastMCP tool for the e·sios glossary."""

from __future__ import annotations

from fastmcp import Context

from esios.api import ESIOS_API_BASE_URL
from glossary.models import GlossarySearchRequest, GlossarySearchResponse
from glossary.service import DEFAULT_GLOSSARY_SERVICE

from .common import mcp_log


async def esios_glossary_search(
    request: GlossarySearchRequest,
    ctx: Context | None = None,
) -> GlossarySearchResponse:
    """Search e·sios terminology and return the structured glossary V1 contract."""
    url = f"{ESIOS_API_BASE_URL}/{request.language}/glossaries"
    await mcp_log(
        ctx,
        "Searching the e·sios glossary",
        extra={"url": url, "language": request.language},
    )
    try:
        response = await DEFAULT_GLOSSARY_SERVICE.search(("esios",), request)
    except Exception as error:
        await mcp_log(
            ctx,
            "e·sios glossary search failed",
            level="error",
            extra={"url": url, "error_type": type(error).__name__},
        )
        raise
    await mcp_log(
        ctx,
        "e·sios glossary search completed",
        extra={
            "url": url,
            "status": "success",
            "candidate_count": len(response.candidates),
        },
    )
    return response
