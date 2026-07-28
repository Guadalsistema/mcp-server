#!/usr/bin/env python3
"""
OMIE MCP Server Entry Point - Final Version
"""

import os
import sys
import asyncio
import logging

from fastmcp import FastMCP

from omie_mcp.tools import marginalpdbc, pdbc


# Register tools
server.add_tool(marginalpdbc)
server.add_tool(pdbc)

# Create MCP server with configured tools
server = FastMCP(
    name="OMIE MCP Server",
    instructions="OMIE data access server providing electricity market data tools"
)

def main():
    logging.basicConfig(level=logging.INFO)
    server.run()

if __name__ == "__main__":
    raise SystemExit(main())
