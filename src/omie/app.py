#!/usr/bin/env python3
"""
OMIE MCP Server Entry Point - Final Version
"""

import logging

from fastmcp import FastMCP

from omie.tools import marginalpdbc, pdbc


server = FastMCP(
    name="OMIE MCP Server",
    instructions="OMIE data access server providing electricity market data tools",
)

server.add_tool(marginalpdbc)
server.add_tool(pdbc)


def main():
    logging.basicConfig(level=logging.INFO)
    # Stdio clients need a fast, quiet handshake; the default banner performs
    # a network update check before the server starts.
    server.run(show_banner=False)


if __name__ == "__main__":
    raise SystemExit(main())
