"""Combined REE and e·sios structured glossary tool."""

from __future__ import annotations

from typing import Any, Literal

from fastmcp import Context

from .models import GlossarySearchRequest, GlossarySearchResponse
from .service import DEFAULT_GLOSSARY_SERVICE


async def _mcp_log(
    ctx: Context | None,
    message: str,
    *,
    level: Literal["info", "error"] = "info",
    extra: dict[str, Any] | None = None,
) -> None:
    if ctx is None or ctx.request_context is None:
        return
    if level == "error":
        await ctx.error(message, logger_name="glossary_mcp", extra=extra)
    else:
        await ctx.info(message, logger_name="glossary_mcp", extra=extra)


async def glossary_search(
    request: GlossarySearchRequest,
    ctx: Context | None = None,
) -> GlossarySearchResponse:
    """Search REE and e·sios together, preserving candidate provenance."""
    await _mcp_log(
        ctx,
        "Searching the combined energy glossaries",
        extra={"sources": ["ree", "esios"], "language": request.language},
    )
    try:
        response = await DEFAULT_GLOSSARY_SERVICE.search(("ree", "esios"), request)
    except Exception as error:
        await _mcp_log(
            ctx,
            "Combined glossary search failed",
            level="error",
            extra={"error_type": type(error).__name__},
        )
        raise
    await _mcp_log(
        ctx,
        "Combined glossary search completed",
        extra={"status": "success", "candidate_count": len(response.candidates)},
    )
    return response
