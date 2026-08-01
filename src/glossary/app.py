#!/usr/bin/env python3
"""Combined glossary MCP server entry point."""

import argparse
import logging
from collections.abc import Sequence

from dotenv import load_dotenv
from fastmcp import FastMCP

from esios.mcp.glossary import esios_glossary_search
from ree.mcp.glossary import ree_glossary_search

from .mcp import glossary_search


load_dotenv()


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


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--asios-api-key",
        "--esios-api-key",
        dest="api_key",
        help="e·sios API key (also accepted from ESIOS_API_KEY)",
    )
    arguments, _ = parser.parse_known_args(argv)
    if arguments.api_key:
        import os

        os.environ["ESIOS_API_KEY"] = arguments.api_key
    logging.basicConfig(level=logging.INFO)
    server.run(show_banner=False)


if __name__ == "__main__":
    raise SystemExit(main())
