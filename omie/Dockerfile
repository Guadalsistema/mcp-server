FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Disable development dependencies
ENV UV_NO_DEV=1

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN uv pip install --system .

EXPOSE 8000

CMD ["omie-mcp"]
