# Fase 1: Base-image met een slanke Python-versie
FROM python:3.12-slim as base

# Voorkom dat Python.pyc-bestanden schrijft en buffer output niet
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Creëer een non-root gebruiker voor beveiliging
RUN addgroup --system app && adduser --system --group app

# Fase 2: Builder-image voor het installeren van afhankelijkheden met uv
FROM base as builder

# Kopieer de uv binary van de officiële distroless image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Stel de werkdirectory in
WORKDIR /app

# Kopieer alleen de dependency-bestanden om Docker's layer caching te benutten
COPY pyproject.toml ./
COPY uv.lock* ./

# Installeer alleen productie-afhankelijkheden in een virtuele omgeving
# --frozen zorgt voor een exacte reproductie van de lockfile
# --no-dev slaat ontwikkelingsafhankelijkheden over
RUN uv sync --frozen --no-dev

# Kopieer de applicatiecode
COPY src/ ./src/

# Fase 3: Productie-image
FROM base as production

WORKDIR /app

# Kopieer de virtuele omgeving en de broncode van de builder-fase
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app/src ./src

# Voeg de venv toe aan het PATH
ENV PATH="/app/.venv/bin:$PATH"

# Verander de eigenaar van de bestanden naar de non-root gebruiker en schakel over
RUN chown -R app:app .
USER app

# Stel het commando in om de applicatie te starten
CMD ["fastmcp", "run", "src.mcp_invoice_processor.main:mcp", "--host", "0.0.0.0", "--port", "8080"]
