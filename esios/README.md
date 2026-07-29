# e·sios MCP Server

This package exposes specialized MCP tools for Red Eléctrica's public e·sios
API. The API documentation is available at
<https://api.esios.ree.es/>.

The implementation is split into two layers:

- `esios_mcp.api` contains framework-independent endpoint clients.
- `esios_mcp.mcp` contains FastMCP tools, validation, error responses, and
  client-visible notifications.

## Authentication

Set the API key in the environment before starting the server:

```powershell
$env:ESIOS_API_KEY = "your-api-key"
```

The key is sent as the `x-api-key` header and is never included in tool
responses or MCP notifications.

## Tools

- `esios_list_indicators`: list available indicators.
- `esios_search_indicators`: search indicators by name.
- `esios_get_indicator`: retrieve one indicator by ID, including values,
  date-range filters, aggregations, and geographical filters.
- `esios_list_widgets`: list Widget V2 resources.
- `esios_get_widget`: retrieve a Widget V2 resource by numeric ID or slug.
- `esios_list_archives`, `esios_get_archive`, and
  `esios_get_archive_calculator_data`: discover archive metadata and calculator
  values.
- `esios_download_archive`: download an archive as base64 with content type and
  size metadata.
- `esios_list_json_archives`, `esios_get_json_archive`, and
  `esios_download_json_archive`: discover and retrieve JSON archive values.
- `esios_list_auctions`: list auctions, optionally by year.
- `esios_list_content`: list maps, documentations, glossaries, news, static
  pages, or UMMs with taxonomy, vocabulary, ordering, and sticky filters.
- `esios_filter_news`: specialized news filtering tool.
- `esios_get_content` and `esios_get_content_by_id`: retrieve content by its
  locale-prefixed slug or shared content ID.
- `esios_get_offer_widget` and `esios_get_offer_indicator`: retrieve offer
  widget and offer-indicator data.
- `esios_search_contents` and `esios_search_contents_and_indicators`: search
  content or combined content and indicator records.

Spanish is the default locale; `en` is also supported. The upstream JSON is
preserved under the response `data` field, with request metadata alongside it.

## Installation and tests

```powershell
cd esios
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
python -m unittest discover -s tests
```

The live tests load `ESIOS_API_KEY` from `.env` with `python-dotenv`, but are
opt-in so ordinary test runs do not call the external API:

```powershell
$env:LIVE_TEST = "1"
python -m unittest discover -s tests -v
```

The local `.env` file is gitignored and excluded from the Docker build context;
`.env.example` documents the required variable without containing credentials.

## Running the server

```powershell
python -m esios_mcp.app
```

## Docker

Build the image from the repository root:

```powershell
docker build -t mcp/esios ./esios
```

The root VS Code MCP configuration starts it with Docker stdio and forwards
the `ESIOS_API_KEY` environment variable.
