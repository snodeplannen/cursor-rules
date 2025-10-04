# MCP Invoice Processor

Een FastMCP server voor het extraheren van gestructureerde data uit PDF-documenten zoals CV's en facturen.

## 🚀 Functies

- **Intelligente Documentverwerking**: Automatische classificatie van CV's en facturen
- **Geavanceerde Tekstextractie**: Hoogwaardige PDF-verwerking met PyMuPDF
- **AI-gestuurde Data-extractie**: Gestructureerde output via Ollama LLM integratie
- **Chunking & Merging**: Ondersteuning voor grote documenten met slimme samenvoeging
- **Type-veilige Configuratie**: Robuuste configuratie met Pydantic
- **Gestructureerde Logging**: JSON logging voor productieomgevingen
- **Dev Container Support**: Reproduceerbare ontwikkelomgeving

## 🏗️ Architectuur

De applicatie is gebouwd volgens moderne Python best practices:

- **src-layout**: Robuuste projectstructuur die packaging-fouten voorkomt
- **Modulaire Pijplijn**: Scheiding van verantwoordelijkheden voor testbaarheid
- **FastMCP Framework**: Moderne MCP server implementatie
- **Docker Support**: Containerisatie voor productie en ontwikkeling

## 📋 Vereisten

- Python 3.10-3.12
- uv package manager
- Ollama server draaiend op localhost:11434
- Docker (optioneel, voor containerisatie)

## 🛠️ Installatie

### 1. Clone de repository

```bash
git clone <repository-url>
cd mcp-invoice-processor
```

### 2. Installeer dependencies met uv

```bash
# Installeer uv als je het nog niet hebt
pip install uv

# Installeer project dependencies
uv sync --dev
```

### 3. Configureer omgevingsvariabelen

```bash
# Kopieer het voorbeeld bestand
cp .env.example .env

# Pas de waarden aan in .env
```

## 🔧 Configuratie

De applicatie gebruikt de volgende omgevingsvariabelen:

| Variabele | Beschrijving | Standaard |
|-----------|---------------|-----------|
| `LOG_LEVEL` | Logging niveau | `INFO` |
| `OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Te gebruiken LLM model | `llama3` |
| `OLLAMA_TIMEOUT` | Timeout in seconden | `120` |

## 🚀 Gebruik

### MCP Configuratie

De applicatie kan worden gebruikt via verschillende MCP configuraties:

#### STDIO Transport (Aanbevolen voor lokale ontwikkeling)
```json
{
  "mcpServers": {
    "mcp-invoice-processor": {
      "command": "C:\\ProgramData\\miniforge3\\Scripts\\uv.exe",
      "args": [
        "--directory",
        "C:\\py_cursor-rules\\cursor_ratsenbergertest\\",
        "run",
        "python",
        "-m",
        "src.mcp_invoice_processor.main"
      ],
      "env": {
        "LOG_LEVEL": "INFO",
        "OLLAMA_HOST": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3"
      }
    }
  }
}
```

**Let op**: Pas de paden aan naar jouw systeem:
- `command`: Absolute pad naar uv executable
- `--directory`: Absolute pad naar je project directory

#### HTTP Transport (Voor netwerk toegang)
```json
{
  "mcpServers": {
    "mcp-invoice-processor-http": {
      "command": "C:\\ProgramData\\miniforge3\\Scripts\\uv.exe",
      "args": [
        "--directory",
        "C:\\py_cursor-rules\\cursor_ratsenbergertest\\",
        "run",
        "fastmcp",
        "run",
        "src.mcp_invoice_processor.main:mcp",
        "--host",
        "127.0.0.1",
        "--port",
        "8080",
        "--transport",
        "http"
      ]
    }
  }
}
```

**Let op**: Pas de paden aan naar jouw systeem:
- `command`: Absolute pad naar uv executable
- `--directory`: Absolute pad naar je project directory

Gebruik `mcp.json` of `mcp-http.json` in je MCP client configuratie.

### Lokale ontwikkeling

```bash
# Start de FastMCP server
uv run python -m src.mcp_invoice_processor.main

# Of gebruik fastmcp CLI
uv run fastmcp run src.mcp_invoice_processor.main:mcp
```

### Met Docker

```bash
# Bouw de container
docker build -t mcp-invoice-processor .

# Start de container
docker run -p 8080:8080 \
  -e OLLAMA_HOST="http://host.docker.internal:11434" \
  -e LOG_LEVEL="DEBUG" \
  mcp-invoice-processor
```

### Dev Container (VS Code)

1. Open het project in VS Code
2. Accepteer de "Reopen in Container" prompt
3. De ontwikkelomgeving wordt automatisch opgezet

## 📊 Monitoring en Observability

De applicatie bevat uitgebreide monitoring en metrics collectie:

### Monitoring Dashboard
```bash
# Start de monitoring dashboard
uv run python -m src.mcp_invoice_processor.monitoring.dashboard

# Dashboard beschikbaar op: http://localhost:8000
```

### Metrics Endpoints
- **`/`** - Real-time monitoring dashboard met auto-refresh
- **`/health`** - Health check endpoint met service status
- **`/metrics`** - JSON metrics voor externe monitoring
- **`/metrics/prometheus`** - Prometheus-compatible metrics export

### Metrics Categorieën
- **Document Processing**: Totaal verwerkte documenten, succes rates, verwerkingstijden, document types
- **Ollama Integration**: LLM request metrics, response tijden, model usage, error rates
- **System Metrics**: Uptime, memory/CPU usage, actieve verbindingen

### Test Metrics Generator
```bash
# Genereer test metrics voor dashboard
uv run python tests/test_metrics_generation.py

# Kies optie 2 voor continue real-time updates
```

## 🧪 Testen

### Unit Tests
```bash
# Voer alle tests uit
uv run pytest

# Voer tests uit met coverage
uv run pytest --cov=src

# Voer specifieke tests uit
uv run pytest tests/test_pipeline.py
```

### MCP Server Tests
```bash
# Test met Python client
uv run python tests/test_mcp_client.py

# Test met shell script (Linux/macOS)
./test_mcp.sh

# Test met PowerShell (Windows)
./test_mcp.ps1
```

### Uitgebreide Tests
```bash
# Alle tests uitvoeren
uv run python tests/run_tests.py

# Specifieke test categorieën
uv run pytest tests/ -m fastmcp -v      # FastMCP tests
uv run pytest tests/ -m mcp -v          # MCP library tests
uv run pytest tests/ -m integration -v  # Integratie tests

# Test rapporten genereren
uv run pytest tests/ --html=tests/report.html --self-contained-html
uv run pytest tests/ --cov=src --cov-report=html
```

### Snelle Verificatie
```bash
# Test server start
uv run python -m src.mcp_invoice_processor.main

# Test FastMCP CLI
uv run fastmcp --help
```

## 📁 Projectstructuur

```
mcp-invoice-processor/
├── .devcontainer/          # VS Code Dev Container configuratie
├── src/
│   └── mcp_invoice_processor/
│       ├── __init__.py
│       ├── main.py         # FastMCP server entry point
│       ├── config.py       # Configuratiebeheer
│       ├── logging_config.py # Logging configuratie
│       └── processing/     # Verwerkingsmodules
│           ├── __init__.py
│           ├── models.py   # Pydantic data modellen
│           ├── pipeline.py # Hoofdverwerkingspijplijn
│           ├── classification.py # Documentclassificatie
│           ├── text_extractor.py # PDF tekstextractie
│           ├── chunking.py # Tekst chunking strategieën
│           └── merging.py  # Samenvoeg- en ontdubbelingslogica
├── tests/                  # Test bestanden
│   ├── __init__.py
│   ├── conftest.py        # Gedeelde fixtures en configuratie
│   ├── test_pipeline.py   # Unit tests voor verwerkingspijplijn
│   ├── test_monitoring.py # Unit tests voor metrics en monitoring
│   ├── test_fastmcp_client.py # FastMCP client tests
│   ├── test_fastmcp_cli.py    # FastMCP CLI tests
│   ├── test_fastmcp_server.py # Direct FastMCP server tests
│   ├── test_fastmcp_direct.py # Direct core logic tests
│   ├── test_mcp_client.py     # MCP library tests
│   ├── test_ollama_integration.py # Ollama integratie tests
│   ├── test_real_documents.py # Tests met echte documenten
│   ├── test_metrics_generation.py # Metrics test data generator
│   ├── run_tests.py       # Test runner script
│   └── README.md          # Test documentatie
├── Dockerfile             # Productie container
├── .dockerignore          # Docker build context uitsluitingen
├── pyproject.toml         # Project configuratie
├── mcp.json               # MCP configuratie (STDIO) - Windows
├── mcp-http.json          # MCP configuratie (HTTP) - Windows
├── mcp-module.json        # MCP configuratie (Module) - Windows
├── test_mcp_client.py     # Python test client
├── test_mcp.sh            # Shell test script
├── test_mcp.ps1           # PowerShell test script
├── MCP_USAGE.md           # Uitgebreide gebruikshandleiding
└── README.md              # Deze file
```

## 🔄 Verwerkingspijplijn

1. **Tekstextractie**: PDF bytes worden omgezet naar tekst met PyMuPDF
2. **Classificatie**: Documenttype wordt bepaald op basis van trefwoorden
3. **Chunking**: Grote documenten worden opgedeeld in beheersbare stukken
4. **AI-extractie**: Ollama LLM extraheert gestructureerde data volgens Pydantic schema's
5. **Merging**: Partiële resultaten worden samengevoegd en ontdubbeld
6. **Validatie**: Output wordt gevalideerd tegen Pydantic modellen

## 🛠️ Beschikbare Tools

### `process_document`
Verwerkt een PDF-document en extraheert gestructureerde data.

**Parameters:**
- `file_content_base64` (string): Base64-gecodeerde PDF-inhoud
- `file_name` (string): Naam van het bestand

**Returns:**
```json
{
  "document_type": "cv|invoice|unknown",
  "data": {
    // Gestructureerde data volgens documenttype
  },
  "status": "success|error",
  "error_message": "Foutmelding indien van toepassing"
}
```

**Voorbeelden:**
- **CV's**: Extraheert naam, email, telefoon, werkervaring, opleiding, vaardigheden
- **Facturen**: Extraheert factuurnummer, totaalbedrag, klantgegevens

## 🔧 FastMCP Features

### MCP Tools
De server biedt de volgende MCP tools:

- **`process_document_text`**: Verwerkt document tekst en extraheert gestructureerde data
- **`process_document_file`**: Verwerkt een document bestand en extraheert gestructureerde data  
- **`classify_document_type`**: Classificeert alleen het document type zonder volledige verwerking
- **`get_metrics`**: Haalt huidige metrics op van de document processor
- **`health_check`**: Voert een health check uit van de service

### MCP Resources
Uitgebreide documentatie via MCP resources:

- **`mcp://document-types`**: Voorbeelden van ondersteunde document types
- **`mcp://extraction-methods`**: Gids voor extractie methodes  
- **`mcp://server-config`**: Server configuratie informatie

### MCP Prompts
Interactieve gidsen voor optimaal gebruik:

- **`document-processing-guide`**: Document verwerking instructies per type
- **`troubleshooting-guide`**: Troubleshooting voor veelvoorkomende problemen

### Extractie Methodes
- **`hybrid`**: Combinatie van JSON schema en prompt parsing (aanbevolen)
- **`json_schema`**: Gestructureerde extractie met JSON schema
- **`prompt_parsing`**: Flexibele extractie met prompt engineering

## 🤖 Ollama Integratie

De applicatie gebruikt Ollama voor AI-gestuurde data-extractie:

- **Gestructureerde Output**: JSON schema's worden gegenereerd uit Pydantic modellen
- **Validatie**: LLM output wordt gevalideerd tegen dezelfde modellen
- **Foutafhandeling**: Robuuste foutafhandeling voor LLM communicatie
- **Configuratie**: Flexibele configuratie van host, model en timeout

## 🐳 Docker

### Dev Container
- Geoptimaliseerd voor ontwikkeling
- Bevat alle ontwikkelingsafhankelijkheden
- Automatische setup van Python omgeving

### Productie Container
- Meerfasige build voor optimale grootte
- Non-root gebruiker voor beveiliging
- Geoptimaliseerd voor runtime prestaties

## 📊 Logging

De applicatie gebruikt gestructureerde JSON logging:

- **Console Output**: JSON-formatted logs voor parsing
- **Configuratie**: Logging niveau configureerbaar via omgevingsvariabelen
- **Context**: FastMCP context integratie voor voortgangsrapportage

## 🧪 Teststrategie

- **Unit Tests**: Pure functies en modellen
- **Integratie Tests**: Volledige pijplijn met gemockte LLM
- **FastMCP Client Tests**: Client integratie in STDIO mode
- **MCP Library Tests**: MCP protocol integratie
- **Mocking**: Ollama client wordt gemockt voor betrouwbare tests
- **Fixtures**: Herbruikbare test data en mocks
- **Test Markers**: Automatische skip van tests bij ontbrekende dependencies

## 🔒 Beveiliging

- **Non-root Containers**: Docker containers draaien als non-root gebruiker
- **Omgevingsvariabelen**: Geheimen worden geïnjecteerd via omgevingsvariabelen
- **Input Validatie**: Alle input wordt gevalideerd via Pydantic
- **Foutafhandeling**: Geen gevoelige informatie in foutmeldingen

## 🚀 Deployment

### Lokale Deployment

#### STDIO Transport (voor Cursor MCP integratie)
```bash
uv run python -m src.mcp_invoice_processor
```

#### HTTP Transport (voor web API gebruik)
```bash
# Optie 1: FastMCP HTTP server met custom routes (AANBEVOLEN)
uv run python -m src.mcp_invoice_processor.http_server

# Optie 2: Met custom host/port
uv run python -m src.mcp_invoice_processor.http_server 0.0.0.0 8080

# Optie 3: Via FastMCP CLI (alleen MCP endpoints)
uv run fastmcp run src.mcp_invoice_processor.fastmcp_server:mcp --transport http --host 0.0.0.0 --port 8080
```

**HTTP Endpoints (Optie 1):**
- `http://localhost:8080/` - Server informatie
- `http://localhost:8080/health` - Health check
- `http://localhost:8080/metrics` - JSON metrics
- `http://localhost:8080/metrics/prometheus` - Prometheus metrics
- `http://localhost:8080/mcp` - MCP protocol endpoint

### Docker Deployment
```bash
docker run -d \
  --name mcp-processor \
  -p 8080:8080 \
  -e OLLAMA_HOST="http://ollama-server:11434" \
  mcp-invoice-processor
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-processor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-processor
  template:
    metadata:
      labels:
        app: mcp-processor
    spec:
      containers:
      - name: mcp-processor
        image: mcp-invoice-processor:latest
        ports:
        - containerPort: 8080
        env:
        - name: OLLAMA_HOST
          value: "http://ollama-service:11434"
```

## 🤝 Bijdragen

1. Fork de repository
2. Maak een feature branch (`git checkout -b feature/amazing-feature`)
3. Commit je wijzigingen (`git commit -m 'Add amazing feature'`)
4. Push naar de branch (`git push origin feature/amazing-feature`)
5. Open een Pull Request

## 📝 Licentie

Dit project is gelicentieerd onder de MIT License - zie het [LICENSE](LICENSE) bestand voor details.

## 📚 Meer Informatie

### Documentatie
- [MCP_USAGE.md](MCP_USAGE.md) - Uitgebreide gebruikshandleiding
- [FastMCP](https://github.com/fastmcp/fastmcp) - Moderne MCP server framework
- [Ollama](https://ollama.ai/) - Lokale LLM server
- [PyMuPDF](https://pymupdf.readthedocs.io/) - Snelle PDF verwerking
- [Pydantic](https://docs.pydantic.dev/) - Data validatie en serialisatie
- [uv](https://docs.astral.sh/uv/) - Snelle Python package manager

### MCP Configuratie Bestanden
- `mcp.json` - STDIO transport configuratie (aanbevolen voor lokale ontwikkeling) - Windows
- `mcp-http.json` - HTTP transport configuratie (voor netwerk toegang) - Windows
- `mcp-module.json` - Module transport configuratie - Windows

**Let op**: Deze configuraties zijn geoptimaliseerd voor Windows. Voor andere besturingssystemen, pas de paden aan in de configuratie bestanden.

#### Paden voor andere systemen:

**macOS/Linux:**
```json
{
  "command": "/usr/local/bin/uv",
  "args": [
    "--directory",
    "/path/to/your/project/",
    "run",
    "python",
    "-m",
    "src.mcp_invoice_processor.main"
  ]
}
```

**Windows (PowerShell):**
```json
{
  "command": "C:\\ProgramData\\miniforge3\\Scripts\\uv.exe",
  "args": [
    "--directory",
    "C:\\path\\to\\your\\project\\",
    "run",
    "python",
    "-m",
    "src.mcp_invoice_processor.main"
  ]
}
```

### Test Scripts
- `tests/test_mcp_client.py` - Python test client voor MCP server
- `test_mcp.sh` - Shell test script (Linux/macOS)
- `test_mcp.ps1` - PowerShell test script (Windows)
- `tests/test_fastmcp_server.py` - Direct FastMCP server tests
- `tests/test_real_documents.py` - Tests met echte document bestanden
- `tests/test_metrics_generation.py` - Metrics test data generator

## 🙏 Dankbetuigingen

- [FastMCP](https://github.com/fastmcp/fastmcp) - Moderne MCP server framework
- [Ollama](https://ollama.ai/) - Lokale LLM server
- [PyMuPDF](https://pymupdf.readthedocs.io/) - Snelle PDF verwerking
- [Pydantic](https://docs.pydantic.dev/) - Data validatie en serialisatie
- [uv](https://docs.astral.sh/uv/) - Snelle Python package manager
