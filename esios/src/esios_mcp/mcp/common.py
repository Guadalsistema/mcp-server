"""Shared FastMCP behavior for e·sios tools."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime as DateTime
from datetime import timezone
from typing import Any, Callable, Literal

from fastmcp import Context
from fastmcp.tools import ToolResult

from esios_mcp.api import EsiosApiError


ESIOS_SOURCE = "e·sios"
LogLevel = Literal["info", "error"]


async def mcp_log(
    ctx: Context | None,
    message: str,
    *,
    level: LogLevel = "info",
    extra: dict[str, Any] | None = None,
) -> None:
    """Send a structured notification only when an MCP session is active."""
    if ctx is None or ctx.request_context is None:
        return

    if level == "error":
        await ctx.error(message, logger_name="esios_mcp", extra=extra)
    else:
        await ctx.info(message, logger_name="esios_mcp", extra=extra)


def json_result(operation: str, request: dict[str, Any], payload: dict[str, Any]) -> str:
    """Wrap the unchanged upstream payload with MCP metadata."""
    return json.dumps(
        {
            "metadata": {
                "source": ESIOS_SOURCE,
                "service": operation,
                "request": request,
                "retrieved_at": DateTime.now(timezone.utc).isoformat(),
            },
            "data": payload,
        },
        indent=2,
        ensure_ascii=False,
    )


def error_result(operation: str, request: dict[str, Any], error: EsiosApiError) -> ToolResult:
    """Return a stable MCP error without leaking upstream HTML or credentials."""
    payload: dict[str, Any] = {
        "error": {
            "source": ESIOS_SOURCE,
            "operation": operation,
            "code": error.code,
            "message": str(error),
            "retryable": error.retryable,
        },
        "request": request,
    }
    if error.status_code is not None:
        payload["error"]["status_code"] = error.status_code
    return ToolResult(
        content=json.dumps(payload, indent=2, ensure_ascii=False),
        is_error=True,
    )


async def run_api_call(
    *,
    ctx: Context | None,
    operation: str,
    url: str,
    request: dict[str, Any],
    call: Callable[[], dict[str, Any]],
) -> str | ToolResult:
    """Run synchronous requests work off the event loop and report its status."""
    await mcp_log(ctx, f"Calling the e·sios {operation}", extra={"url": url, "params": request})
    try:
        payload = await asyncio.to_thread(call)
    except EsiosApiError as error:
        await mcp_log(
            ctx,
            f"e·sios {operation} call failed",
            level="error",
            extra={
                "url": url,
                "code": error.code,
                "status_code": error.status_code,
                "retryable": error.retryable,
            },
        )
        return error_result(operation, request, error)

    await mcp_log(
        ctx,
        f"e·sios {operation} call completed",
        extra={"url": url, "status": "success"},
    )
    return json_result(operation, request, payload)


def validate_locale(locale: str) -> str:
    if locale not in {"es", "en"}:
        raise ValueError("locale must be one of: en, es")
    return locale


def validate_date_range(start_date: str | None, end_date: str | None) -> None:
    if (start_date is None) != (end_date is None):
        raise ValueError("start_date and end_date must be supplied together")
    if start_date is None or end_date is None:
        return

    try:
        start = DateTime.fromisoformat(start_date.replace("Z", "+00:00"))
        end = DateTime.fromisoformat(end_date.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("start_date and end_date must use ISO 8601 format") from error
    if start > end:
        raise ValueError("start_date must be on or before end_date")


def validate_indicator_id(indicator_id: int) -> int:
    if isinstance(indicator_id, bool) or not isinstance(indicator_id, int) or indicator_id <= 0:
        raise ValueError("indicator_id must be a positive integer")
    return indicator_id


def validate_widget_identifier(widget_id_or_slug: int | str) -> str:
    if isinstance(widget_id_or_slug, bool):
        raise ValueError("widget_id_or_slug must be a positive integer or non-empty slug")
    if isinstance(widget_id_or_slug, int):
        if widget_id_or_slug <= 0:
            raise ValueError("widget_id_or_slug must be a positive integer or non-empty slug")
        return str(widget_id_or_slug)
    if not isinstance(widget_id_or_slug, str) or not widget_id_or_slug.strip():
        raise ValueError("widget_id_or_slug must be a positive integer or non-empty slug")
    return widget_id_or_slug.strip()
