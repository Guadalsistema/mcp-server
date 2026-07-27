#!/usr/bin/env python3
"""
OMIE MCP Server Entry Point - Final Version
"""

import os
import sys
import asyncio
import logging
from fastmcp import FastMCP

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the tools
from omie_mcp.tools import marginalpdbc, pdbc

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    print("OMIE MCP Server initializing...")
    
    # Create MCP server with configured tools
    server = FastMCP(
        name="OMIE MCP Server",
        instructions="OMIE data access server providing electricity market data tools"
    )
    
    # Register tools
    server.add_tool(marginalpdbc)
    server.add_tool(pdbc)
    
    # Print available tools
    print("OMIE MCP Server initialized")
    print("Available tools:")
    print("- marginalpdbc")
    print("- pdbc")
    
    print("Starting server on port 8000...")
    
    # This is the key fix - run the server in a persistent way
    try:
        # The server should run continuously until explicitly stopped
        # This is the standard pattern for FastMCP servers
        asyncio.run(server.run_http_async(port=8000, show_banner=False))
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()