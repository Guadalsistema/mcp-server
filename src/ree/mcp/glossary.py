"""FastMCP tool for the REE glossary resource."""

from __future__ import annotations

from fastmcp import Context

from glossary.models import GlossarySearchRequest, GlossarySearchResponse
from glossary.service import DEFAULT_GLOSSARY_SERVICE
from ree.api import REE_GLOSSARY_URLS
from .common import mcp_log


async def ree_glossary_search(
    request: GlossarySearchRequest,
    ctx: Context | None = None,
) -> GlossarySearchResponse:
    """Search REE terminology and return the structured glossary V1 contract."""
    url = REE_GLOSSARY_URLS[request.language]
    await mcp_log(
        ctx,
        "Searching the REE glossary",
        extra={"url": url, "language": request.language},
    )
    try:
        response = await DEFAULT_GLOSSARY_SERVICE.search(("ree",), request)
    except Exception as error:
        await mcp_log(
            ctx,
            "REE glossary search failed",
            level="error",
            extra={"url": url, "error_type": type(error).__name__},
        )
        raise
    await mcp_log(
        ctx,
        "REE glossary search completed",
        extra={
            "url": url,
            "status": "success",
            "candidate_count": len(response.candidates),
        },
    )
    return response
