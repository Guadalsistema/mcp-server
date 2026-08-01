# OMIE MCP Tools

This package implements OMIE (Spanish Electricity Market Operator) data as MCP (Model Control Protocol) tools. These tools provide access to historical electricity market data from OMIE through standardized MCP interfaces.

## Features

- **Caching**: no persistent cache is enabled in the current unified tree
- **Live Data Access**: Server always accesses live OMIE data (tests can override this)
- **Multiple Data Types**: Support for various OMIE data products
- **Standard MCP Interface**: Compliant with MCP protocol for AI agent consumption

## Tools

### Available Tools

1. **marginalpdbc** - Day-ahead market hourly prices in Spain
2. **pdbc** - Basic matching process data for Spanish electricity market

### Tool Parameters

All tools accept:
- `since`: Start date in ISO `YYYY-MM-DD` format (optional)
- `until`: End date in ISO `YYYY-MM-DD` format (optional)

### Example Usage

```python
# Using the marginalpdbc tool
result = marginalpdbc(since="2023-03-01", until="2023-03-07")

# Using the pdbc tool  
result = pdbc(since="2023-03-01", until="2023-03-07")
```

## Implementation Details

### Live Data Access

The server always accesses live OMIE data. Tests that need to use mock data should set `LIVE_TEST=0`.

### Data Format

All tools return JSON with the following structure:
```json
{
  "metadata": {
    "source": "OMIE",
    "product": "tool_name",
    "since": "YYYY-MM-DD",
    "until": "YYYY-MM-DD",
    "retrieved_at": "ISO timestamp",
    "count": integer
  },
  "data": [
    {
      "date": "YYYY-MM-DD",
      "period": integer,
      "marginal_pt": float,
      "marginal_es": float,
      "currency": "EUR/MWh"
    }
  ]
}
```

The `pdbc` rows use the named columns `unit_code`, `assigned_power`, `unused`,
`offer_type`, and `offer_number`, with `power_unit` set to `MW`. Both responses
include `metadata.column_map`, mapping each source column index to its name.

`marginalpdbc` downloads the daily files that cover the requested range.
`pdbc` downloads one monthly ZIP archive for each month that intersects the
requested range, then returns only rows inside the requested dates.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pytest tests/omie
```

## Running the Server

```powershell
python -m omie_mcp.app
```

The server will start on port 8000 and expose the OMIE tools via the MCP protocol.

## Development

New tools can be added by:
1. Creating a new `.py` file in `src/omie_mcp/tools/`
2. Implementing the tool function with the same signature pattern
3. Adding the tool to the `__init__.py` exports
