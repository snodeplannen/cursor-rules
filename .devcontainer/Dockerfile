# Dev Container Dockerfile voor MCP Invoice Processor
FROM python:3.12-slim

# Installeer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Creëer een non-root gebruiker voor de ontwikkeling
RUN useradd -m vscode
USER vscode
WORKDIR /workspaces/mcp-invoice-processor

# Kopieer dependency-bestanden en installeer alles
# De postCreateCommand in devcontainer.json zal dit doen,
# maar het kan hier worden gedaan om de setup te versnellen.
COPY --chown=vscode:vscode pyproject.toml uv.lock*./
RUN uv sync --dev

# De broncode wordt door VS Code gemount, dus hoeft niet gekopieerd te worden.
