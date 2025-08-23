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

## 🧪 Testen

```bash
# Voer alle tests uit
uv run pytest

# Voer tests uit met coverage
uv run pytest --cov=src

# Voer specifieke tests uit
uv run pytest tests/test_pipeline.py
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
├── Dockerfile             # Productie container
├── .dockerignore          # Docker build context uitsluitingen
├── pyproject.toml         # Project configuratie
└── README.md              # Deze file
```

## 🔄 Verwerkingspijplijn

1. **Tekstextractie**: PDF bytes worden omgezet naar tekst met PyMuPDF
2. **Classificatie**: Documenttype wordt bepaald op basis van trefwoorden
3. **Chunking**: Grote documenten worden opgedeeld in beheersbare stukken
4. **AI-extractie**: Ollama LLM extraheert gestructureerde data volgens Pydantic schema's
5. **Merging**: Partiële resultaten worden samengevoegd en ontdubbeld
6. **Validatie**: Output wordt gevalideerd tegen Pydantic modellen

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
- **Mocking**: Ollama client wordt gemockt voor betrouwbare tests
- **Fixtures**: Herbruikbare test data en mocks

## 🔒 Beveiliging

- **Non-root Containers**: Docker containers draaien als non-root gebruiker
- **Omgevingsvariabelen**: Geheimen worden geïnjecteerd via omgevingsvariabelen
- **Input Validatie**: Alle input wordt gevalideerd via Pydantic
- **Foutafhandeling**: Geen gevoelige informatie in foutmeldingen

## 🚀 Deployment

### Lokale Deployment
```bash
uv run fastmcp run src.mcp_invoice_processor.main:mcp --host 0.0.0.0 --port 8080
```

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

## 🙏 Dankbetuigingen

- [FastMCP](https://github.com/fastmcp/fastmcp) - Moderne MCP server framework
- [Ollama](https://ollama.ai/) - Lokale LLM server
- [PyMuPDF](https://pymupdf.readthedocs.io/) - Snelle PDF verwerking
- [Pydantic](https://docs.pydantic.dev/) - Data validatie en serialisatie
- [uv](https://docs.astral.sh/uv/) - Snelle Python package manager
