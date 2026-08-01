#!/usr/bin/env python3
"""e·sios MCP server entry point."""

import logging

from fastmcp import FastMCP

from esios.mcp import (
    esios_download_archive,
    esios_download_json_archive,
    esios_filter_news,
    esios_get_archive,
    esios_get_archive_calculator_data,
    esios_get_cached_widget_datetime,
    esios_get_content,
    esios_get_content_by_id,
    esios_get_indicator,
    esios_get_json_archive,
    esios_get_offer_indicator,
    esios_get_offer_widget,
    esios_get_widget,
    esios_glossary_search,
    esios_list_archives,
    esios_list_auctions,
    esios_list_content,
    esios_list_indicators,
    esios_list_json_archives,
    esios_list_widgets,
    esios_search_contents,
    esios_search_contents_and_indicators,
    esios_search_indicators,
)


server = FastMCP(
    name="e·sios MCP Server",
    instructions=(
        "e·sios API access server providing specialized tools for discovering "
        "indicators, Widget V2 resources, archives, auctions, content, and search"
    ),
)

server.add_tool(esios_list_indicators)
server.add_tool(esios_search_indicators)
server.add_tool(esios_get_indicator)
server.add_tool(esios_list_widgets)
server.add_tool(esios_get_widget)
server.add_tool(esios_list_archives)
server.add_tool(esios_get_archive)
server.add_tool(esios_get_archive_calculator_data)
server.add_tool(esios_download_archive)
server.add_tool(esios_list_json_archives)
server.add_tool(esios_get_json_archive)
server.add_tool(esios_download_json_archive)
server.add_tool(esios_list_auctions)
server.add_tool(esios_get_cached_widget_datetime)
server.add_tool(esios_list_content)
server.add_tool(esios_filter_news)
server.add_tool(esios_get_content)
server.add_tool(esios_get_content_by_id)
server.add_tool(esios_get_offer_widget)
server.add_tool(esios_get_offer_indicator)
server.add_tool(esios_search_contents)
server.add_tool(esios_search_contents_and_indicators)
server.add_tool(esios_glossary_search)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    server.run(show_banner=False)


if __name__ == "__main__":
    raise SystemExit(main())
