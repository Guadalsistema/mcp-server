# MCP Server Monorepo

Unified repository for the three MCP servers in this workspace:

- `ree_mcp`
- `esios_mcp`
- `omie_mcp`

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

Build from the repository root, for example:

```bash
docker build -f docker/ree -t mcp/ree .
docker build -f docker/esios -t mcp/esios .
docker build -f docker/omie -t mcp/omie .
```
