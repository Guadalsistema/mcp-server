#!/usr/bin/env python3
"""e·sios MCP server entry point."""

import logging

from fastmcp import FastMCP

from esios_mcp.mcp import (
    esios_get_indicator,
    esios_get_widget,
    esios_list_indicators,
    esios_list_widgets,
    esios_search_indicators,
)


server = FastMCP(
    name="e·sios MCP Server",
    instructions=(
        "e·sios API access server providing specialized tools for discovering "
        "indicators, retrieving indicator values, and reading Widget V2 resources"
    ),
)

server.add_tool(esios_list_indicators)
server.add_tool(esios_search_indicators)
server.add_tool(esios_get_indicator)
server.add_tool(esios_list_widgets)
server.add_tool(esios_get_widget)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    server.run(show_banner=False)


if __name__ == "__main__":
    raise SystemExit(main())
