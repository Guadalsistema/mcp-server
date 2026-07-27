# OMIE MCP Tools

This package implements OMIE (Spanish Electricity Market Operator) data as MCP (Model Control Protocol) tools. These tools provide access to historical electricity market data from OMIE through standardized MCP interfaces.

## Features

- **Caching**: SQLite-based in-memory caching to reduce expensive OMIE API calls
- **Live Data Access**: Server always accesses live OMIE data (tests can override this)
- **Multiple Data Types**: Support for various OMIE data products
- **Standard MCP Interface**: Compliant with MCP protocol for AI agent consumption

## Tools

### Available Tools

1. **marginalpdbc** - Day-ahead market hourly prices in Spain
2. **pdbc** - Basic matching process data for Spanish electricity market

### Tool Parameters

All tools accept:
- `since`: Start date in YYYYMMDD format (optional)
- `until`: End date in YYYYMMDD format (optional)

### Example Usage

```python
# Using the marginalpdbc tool
result = marginalpdbc(since="20230301", until="20230307")

# Using the pdbc tool  
result = pdbc(since="20230301", until="20230307")
```

## Implementation Details

### Caching Strategy

- Uses SQLite in-memory database (`omie_cache.db`)
- Cache key format: `{tool_name}_{since}_{until}`
- Default TTL: 1 hour (3600 seconds)
- Cache is used to reduce redundant requests to OMIE server

### Live Data Access

The server always accesses live OMIE data. Tests that need to use mock data should set `LIVE_TEST=0`.

### Data Format

All tools return JSON with the following structure:
```json
{
  "metadata": {
    "source": "OMIE",
    "product": "tool_name",
    "since": "YYYYMMDD",
    "until": "YYYYMMDD",
    "retrieved_at": "ISO timestamp",
    "count": integer
  },
  "data": [
    {
      "date": "YYYYMMDD",
      "hour": integer,
      "price1": float,
      "price2": float,
      "currency": "EUR/MWh"
    }
  ]
}
```

## Installation

```bash
# Activate virtual environment
cd /home/johnny/git/mcp-server/main/omie
source .venv/bin/activate

# Install in development mode
pip install -e .
```

## Running the Server

```bash
# Start the MCP server (always uses live data)
python src/omie_mcp/app.py
```

The server will start on port 8000 and expose the OMIE tools via the MCP protocol.

## Development

New tools can be added by:
1. Creating a new `.py` file in `src/omie_mcp/tools/`
2. Implementing the tool function with the same signature pattern
3. Adding the tool to the `__init__.py` exports