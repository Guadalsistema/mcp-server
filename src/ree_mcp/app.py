#!/usr/bin/env python3
"""REE MCP server entry point."""

import logging

from fastmcp import FastMCP

from ree_mcp.tools import ree_data, ree_glossary


server = FastMCP(
    name="REE MCP Server",
    instructions="REE data access server providing Red Electrica REData tools",
)

server.add_tool(ree_data)
server.add_tool(ree_glossary)


def main():
    logging.basicConfig(level=logging.INFO)
    server.run(show_banner=False)


if __name__ == "__main__":
    raise SystemExit(main())
