"""Shared FastMCP behavior for REE tools."""

from __future__ import annotations

import json
from typing import Any, Literal

from fastmcp import Context


async def mcp_log(
    ctx: Context | None,
    message: str,
    *,
    level: Literal["info", "error"] = "info",
    extra: dict[str, Any] | None = None,
) -> None:
    if ctx is None or ctx.request_context is None:
        return
    if level == "error":
        await ctx.error(message, logger_name="ree_mcp", extra=extra)
    else:
        await ctx.info(message, logger_name="ree_mcp", extra=extra)


def json_result(metadata: dict[str, Any], data: Any) -> str:
    return json.dumps({"metadata": metadata, "data": data}, indent=2, ensure_ascii=False)
