# MCP Server - Omie Integration

This repository contains the implementation of an MCP (Model Control Protocol) server that connects AI agents with Omie's energy market data resources.

## Project Structure

```
.
├── pyproject.toml
├── Dockerfile
├── tests
├── src/               # Omie MCP server package
│   ├── app.py         # Main server entrypoint
│   └── tools/         # Tool implementations
│       ├── __init__.py
│       ├── base_tool.py
│       └── marginalpdbc.py
└── README.md          # This file
```

## Omie MCP Server

The Omie MCP server provides access to Omie's energy market data through the MCP protocol. Currently, it supports retrieving OMIE data including:

- Marginal price data (marginalpdbc)
- Other OMIE market data products

## Deployment

The Omie MCP server can be containerized using the provided Dockerfile:

```bash
docker build -t omie-mcp .
docker run -p 8000:8000 omie-mcp
```

## Usage

Once running, the server exposes tools that can be invoked by AI agents:
- `marginalpdbc(since="20230307", until="20230307")` - Get marginal price data for specific dates

## Development

To develop locally:
1. Create a virtual environment
2. Install dependencies: `pip install -e .`
3. Run the server: `python -m src.app`
