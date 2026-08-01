# REE MCP Tools

This package exposes Red Electrica's public REData API and glossary as MCP
tools. The API documentation is available at
<https://www.ree.es/es/datos/apidatos>; glossary definitions come from
<https://www.ree.es/es/glosario>.

## Tools

### `ree_data`

Retrieves any documented REData widget. The category and widget are the URL
segments from the API documentation.

Required parameters:

- `category`: `balance`, `demanda`, `generacion`, `intercambios`, `mercados`, or
  `transporte`
- `widget`: for example `balance-electrico` or `estructura-generacion`
- `start_date` and `end_date`: `YYYY-MM-DDTHH:MM`

Optional parameters:

- `time_trunc`: `hour`, `day`, `month`, or `year` (default `day`)
- `lang`: `es` or `en` (default `es`)
- `geo_trunc`, `geo_limit`, and `geo_ids`: provide all three for a regional
  query. `geo_trunc` must be `electric_system`; use `ccaa` as `geo_limit` for
  an autonomous community and pass its numeric ID in `geo_ids`.

The tool validates the category-widget relationship before calling REE. For
example, `potencia-maxima-instantanea` belongs to the `generacion` category,
not `demanda`. The `demanda-tiempo-real` name is not a REData widget; regional
real-time curves are provided by REE's separate Visiona service.

Example:

```python
import asyncio

from ree.mcp.data import ReeDataInput, ree_data

asyncio.run(
    ree_data(
        ReeDataInput(
            category="balance",
            widget="balance-electrico",
            start_date="2019-01-01T00:00",
            end_date="2019-01-31T23:59",
            time_trunc="day",
        )
    )
)
```

The response keeps the API's JSON:API-shaped payload under `data` and adds a
`metadata` object containing the request details.

If REE is unavailable or returns an upstream error, the tool returns the MCP
error result with `isError: true`. Its text payload contains a stable error
`code`, a user-facing `message`, the HTTP `status_code` when available, and a
`retryable` flag. Upstream HTML error pages are never exposed to the caller.

Each tool sends FastMCP `info` notifications when an REE request starts and
completes. Failed upstream requests send an `error` notification. Messages
include structured request URL, parameters, status, and error metadata for MCP
clients that support server logging.

### `ree_glossary_search`

Searches the cached public glossary using a structured request and returns the
shared `GlossarySearchResponse` directly. Matching is deterministic,
case- and accent-insensitive, and classifies exact, alias, prefix/token, and
definition matches. The legacy `ree_glossary` JSON-string tool has been
removed; use `ree_glossary_search` for all glossary lookups.

## Installation and tests

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python -m pytest tests/ree
$env:LIVE_TEST = "1"
python -m pytest tests/ree/test_live.py
```

The live suite makes one real request for each exposed tool.

## Running the server

```bash
python -m ree.app
```
