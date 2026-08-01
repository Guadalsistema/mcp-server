# MCP Server Monorepo

Unified repository for the four MCP servers in this workspace:

- `ree-mcp`
- `esios-mcp`
- `omie-mcp`
- `glossary-mcp`, combining the REE and e·sios glossaries

All Python packages now live under the root [`src/`](./src), tests live under
[`tests/`](./tests), and container definitions live under [`docker/`](./docker).

## Development

Create one virtual environment at the repository root and install the project in
editable mode:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
```

Run the full test suite from the repository root:

```bash
python -m pytest tests
```

Optional live tests remain opt-in:

- Set `LIVE_TEST=1` to enable REE and OMIE live checks.
- Set `LIVE_TEST=1` and `ESIOS_API_KEY` to enable ESIOS live checks.

## Docker

Each server has a dedicated Dockerfile under [`docker/`](./docker):

- `docker/ree`
- `docker/esios`
- `docker/omie`
- `docker/glossary`

Build from the repository root, for example:

```bash
docker build -f docker/ree -t mcp/ree .
docker build -f docker/esios -t mcp/esios .
docker build -f docker/omie -t mcp/omie .
docker build -f docker/glossary -t mcp/glossary .
```

`mcp/esios` and `mcp/glossary` require `ESIOS_API_KEY` at runtime. The
glossary server exposes `glossary_search`, `ree_glossary_search`, and
`esios_glossary_search` as structured-output tools.
