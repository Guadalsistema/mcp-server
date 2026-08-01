#!/usr/bin/env python3
"""Combined glossary MCP server entry point."""

import logging

from fastmcp import FastMCP

from esios.mcp.glossary import esios_glossary_search
from ree.mcp.glossary import ree_glossary_search

from .mcp import glossary_search


server = FastMCP(
    name="Energy Glossary MCP Server",
    instructions=(
        "Structured terminology search across the authoritative REE and e·sios "
        "energy glossaries"
    ),
)

server.add_tool(glossary_search)
server.add_tool(ree_glossary_search)
server.add_tool(esios_glossary_search)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    server.run(show_banner=False)


if __name__ == "__main__":
    raise SystemExit(main())
