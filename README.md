# MCP Document Processor

Een moderne, volledig generieke FastMCP server voor intelligente document verwerking met AI-powered extractie.

## 🚀 Volledig Generieke Architecture (v2.1)

**Volledig gerefactored** naar een plugin-gebaseerde processor architecture met:
- ✅ **Volledig Generiek**: FastMCP server bevat geen hardcoded document types
- ✅ **Dynamische Tools**: Tools worden automatisch gegenereerd op basis van processors
- ✅ **Dynamische Documentatie**: Alle prompts en voorbeelden komen van processors
- ✅ **Async Everywhere**: Volledige async/await support
- ✅ **FastMCP Best Practices**: Context, Resources, Annotations, Progress
- ✅ **Modulair**: Elk documenttype is een zelfstandige processor
- ✅ **Uitbreidbaar**: Nieuw type = nieuwe folder + registratie
- ✅ **Parallel Processing**: Async parallel classification
- ✅ **Statistics**: Realtime metrics per processor

---

## 🎯 Functies

### Document Processing
- **📋 Invoice/Factuur Processing**: Automatische extractie van factuurnummers, bedragen, BTW, line items
- **👤 CV/Resume Processing**: Extractie van persoonlijke gegevens, werkervaring, opleiding, vaardigheden
- **🔌 Volledig Uitbreidbaar**: Nieuwe documenttypes vereisen geen server wijzigingen
- **🎯 Dynamische Tools**: Processor-specifieke MCP tools worden automatisch gegenereerd

### AI & Extraction
- **🤖 Ollama Integration**: Lokale LLM voor data extractie
- **🎯 Hybrid Mode**: Combineert JSON schema + prompt parsing voor beste resultaten
- **📊 JSON Schema Mode**: Structured outputs via Ollama
- **💬 Prompt Parsing**: Flexibele extractie voor complexe documenten

### Monitoring & Observability
- **📈 Realtime Statistics**: Per-processor en global metrics
- **📊 Progress Reporting**: Live updates tijdens verwerking
- **🔍 Health Checks**: Ollama connectie en system status
- **📝 Structured Logging**: Comprehensive logging met metadata

### Performance
- **⚡ Parallel Classification**: Alle processors classificeren tegelijkertijd
- **🚀 Async I/O**: Non-blocking operations
- **💪 Chunking Support**: Grote documenten in behapbare stukken
- **🔄 Smart Merging**: Fuzzy deduplication van resultaten

---

## 🏗️ Architectuur

### Modulaire Processor System

```
processors/
├── base.py                    # BaseDocumentProcessor interface
├── registry.py                # ProcessorRegistry (singleton)
├── invoice/                   # 📋 Invoice Processor
│   ├── models.py              # InvoiceData, InvoiceLineItem
│   ├── prompts.py             # Extraction prompts
│   └── processor.py           # InvoiceProcessor implementation
└── cv/                        # 👤 CV Processor  
    ├── models.py              # CVData, WorkExperience, Education
    ├── prompts.py             # Extraction prompts
    └── processor.py           # CVProcessor implementation
```

### BaseDocumentProcessor Interface

Elk processor implementeert:
- **Classificatie**: Keywords + async confidence scoring
- **Data Models**: Pydantic models + JSON schemas
- **Prompts**: Voor alle extractie methoden
- **Extractie**: Async extraction met progress reporting
- **Merging**: Voor gechunkte documenten
- **Validatie**: Quality checks + completeness scoring
- **Statistics**: Custom metrics per type
- **Tool Metadata**: FastMCP annotations en beschrijvingen
- **Tool Examples**: Voorbeelden en documentatie voor dynamische generatie

### ProcessorRegistry

Centraal management voor:
- Processor registratie
- **Parallel async classificatie** (alle processors tegelijk!)
- Global statistics aggregatie
- MCP Resources automatische registratie
- **Dynamische tool registratie** op basis van processors

---

## 📋 Vereisten

- Python 3.10-3.12
- uv package manager
- Ollama server draaiend op localhost:11434
- Docker (optioneel, voor containerisatie)

---

## 🛠️ Installatie

### 1. Clone Repository

```bash
git clone <repository-url>
cd cursor_ratsenbergertest
```

### 2. Installeer Dependencies

```bash
# Installeer uv (als nog niet geïnstalleerd)
pip install uv

# Installeer project dependencies
uv sync --dev
```

### 3. Configureer Ollama

```bash
# Download en start Ollama
ollama pull llama3.2

# Verificeer dat Ollama draait
curl http://localhost:11434/api/tags
```

---

## 🚀 Quick Start Scripts

Na installatie kun je de servers eenvoudig starten via de geïnstalleerde scripts:

### MCP Servers

```bash
# STDIO transport (voor Cursor Desktop integratie)
uv run mcp-server

# HTTP transport (voor web applicaties)
uv run mcp-http-server

# HTTP transport met custom monitoring routes
uv run mcp-http-server-async
```

### MCP Client Demos

```bash
# Volledige client demo (alle transports)
uv run mcp-client-demo

# Eenvoudige HTTP client demo
uv run mcp-http-client
```

### Development Scripts

```bash
# Voer alle tests uit
uv run test-mcp
```

### Custom Configuratie

```bash
# HTTP server op custom host/port
uv run python src/mcp_invoice_processor/fastmcp_http_server.py 0.0.0.0 9000

# HTTP server met monitoring routes
uv run python src/mcp_invoice_processor/http_server.py 127.0.0.1 8080
```

### Server Endpoints (HTTP Mode)

- **MCP Tools**: `http://127.0.0.1:8000/mcp/`
- **Health Check**: `http://127.0.0.1:8000/health`
- **Metrics**: `http://127.0.0.1:8000/metrics`
- **Prometheus Metrics**: `http://127.0.0.1:8000/metrics/prometheus`

---

## 🧪 MCP Client Demos

Het project bevat uitgebreide client demos die laten zien hoe je de MCP server kunt gebruiken:

### Volledige Client Demo

De `example_mcp_client.py` demonstreert alle transport methodes:

```bash
# Start de volledige demo
uv run mcp-client-demo
```

**Deze demo test:**
- ✅ **Direct Tools**: Directe aanroep van tools zonder MCP protocol
- ✅ **File Processing**: Verwerking van tekst bestanden
- ✅ **HTTP Transport**: Client-server communicatie via HTTP
- ✅ **STDIO Transport**: Client-server communicatie via stdin/stdout
- ✅ **Health Checks**: Server status monitoring
- ✅ **Metrics**: Performance metrics ophalen

### Eenvoudige HTTP Client

De `simple_http_client.py` toont een uitgebreide HTTP client met real-world documenten:

```bash
# Start de uitgebreide HTTP demo
uv run mcp-http-client
```

**Deze demo test:**
- ✅ **HTTP Connection**: Verbinding met HTTP server
- ✅ **Health Check**: Server status controleren
- ✅ **Text Invoice Processing**: Factuur tekst verwerking
- ✅ **Text CV Processing**: CV tekst verwerking
- ✅ **PDF CV Processing**: Echte PDF CV (`martin-ingescande-CV-losvanbrief-sikkieversie5.pdf`)
- ✅ **PDF Invoice Processing**: Echte Amazon factuur PDF (`amazon_rugtas-factuur.pdf`)
- ✅ **Metrics**: Server statistieken

### Real-World Test Resultaten

De uitgebreide HTTP client test toont uitstekende resultaten met echte documenten:

**📄 PDF CV Processing:**
- ✅ **Naam**: M. Hartog, Martin (echte naam uit PDF!)
- ✅ **Werkervaring**: 8 posities (veel meer dan tekst CV)
- ✅ **Opleiding**: 4 diploma's
- ✅ **Skills**: 12 vaardigheden
- ✅ **Confidence**: 70%
- ✅ **Processing Time**: ~18 seconden

**🧾 PDF Invoice Processing:**
- ✅ **Invoice ID**: DS-AEU-INV-NL-2024-2198743 (echte Amazon factuur ID!)
- ✅ **Supplier**: Amazon EU S.à r.l. (correcte Amazon entiteit)
- ✅ **Customer**: Korper ICT (echte klant naam)
- ✅ **Total Amount**: €154.43 (correcte bedragen)
- ✅ **Confidence**: 100%
- ✅ **Processing Time**: ~5 seconden

### Client Voorbeelden

**HTTP Client Code:**
```python
from fastmcp import Client

async def test_client():
    async with Client("http://127.0.0.1:8000/mcp") as client:
        # Health check
        health = await client.call_tool("health_check", {})
        
        # Text document processing
        result = await client.call_tool("process_document_text", {
            "text": "FACTUUR\nFactuurnummer: INV-001\nTotaal: €100",
            "extraction_method": "json_schema"
        })
        
        # PDF document processing
        pdf_result = await client.call_tool("process_document_file", {
            "file_path": "martin-ingescande-CV-losvanbrief-sikkieversie5.pdf",
            "extraction_method": "hybrid"
        })
```

**Direct Tools Code:**
```python
from mcp_invoice_processor import tools

async def test_direct():
    # Direct tool usage
    health = await tools.health_check()
    result = await tools.process_document_text(text, "hybrid")
    metrics = await tools.get_metrics()
```

---

### Via MCP Client (Cursor)

Configureer in Cursor settings (`mcp_config_cursor.json`):

```json
{
  "mcpServers": {
    "document-processor": {
      "command": "uv",
      "args": [
        "run",
        "mcp-server"
      ],
      "cwd": "C:\\py_cursor-rules\\cursor_ratsenbergertest\\"
    }
  }
}
```

**Of gebruik de nieuwe script:**
```json
{
  "mcpServers": {
    "document-processor": {
      "command": "uv",
      "args": [
        "run",
        "mcp-server"
      ]
    }
  }
}
```

### Programmatisch

```python
from mcp_invoice_processor.processors import get_registry
from mcp_invoice_processor.processors.invoice import InvoiceProcessor
from mcp_invoice_processor.processors.cv import CVProcessor

# Initialiseer registry
registry = get_registry()
registry.register(InvoiceProcessor())
registry.register(CVProcessor())

# Classificeer document (parallel!)
doc_type, confidence, processor = await registry.classify_document(text, ctx)

# Extraheer data
if processor:
    data = await processor.extract(text, ctx, method="hybrid")
    print(f"Type: {doc_type}, Confidence: {confidence}%")
    print(f"Data: {data.model_dump()}")
```

---

## 🔧 MCP Tools

### Dynamisch Gegenereerde Tools

De FastMCP server genereert automatisch tools op basis van beschikbare processors:

#### Algemene Tools
- **`process_document_text`**: Verwerk document tekst met automatische type detectie
- **`process_document_file`**: Verwerk document bestand (TXT, PDF)
- **`classify_document_type`**: Classificeer document zonder volledige verwerking
- **`get_metrics`**: Comprehensive metrics van alle processors
- **`health_check`**: System en Ollama status check

#### Processor-Specifieke Tools (Dynamisch)
- **`process_invoice`**: Invoice-specifieke verwerking (gegenereerd door InvoiceProcessor)
- **`process_cv`**: CV-specifieke verwerking (gegenereerd door CVProcessor)
- **`process_[type]`**: Automatisch gegenereerd voor elk nieuw documenttype

### Tool Parameters

**Algemene Parameters:**
- `text` (str): Document tekst
- `extraction_method` (str): "hybrid", "json_schema", of "prompt_parsing"
- `model` (str, optional): Ollama model naam voor extractie

**File Processing:**
- `file_path` (str): Pad naar document bestand

---

## 📊 MCP Resources

### Dynamisch Gegenereerde Resources

Processors exposen automatisch resources en de server genereert dynamische documentatie:

#### Processor Resources
```
stats://invoice      → Invoice processor statistics
stats://cv           → CV processor statistics
stats://all          → Global statistics

schema://invoice     → InvoiceData JSON schema
schema://cv          → CVData JSON schema

keywords://invoice   → Invoice classification keywords
keywords://cv        → CV classification keywords
```

#### Dynamische Documentatie
```
mcp://document-types → Dynamisch gegenereerde voorbeelden van alle document types
```

**Gebruik via MCP client:**
```python
# LLM kan statistics opvragen
stats = await read_resource("stats://invoice")

# LLM kan documentatie opvragen
docs = await read_resource("mcp://document-types")
```

---

## 🧪 Testing

### Run Tests

```bash
# Nieuwe processor tests
uv run pytest tests/test_processors.py -v

# Updated pipeline tests
uv run pytest tests/test_pipeline.py -v

# Alle moderne tests (exclude legacy)
uv run pytest tests/ --ignore=tests/legacy_tests -v

# Met coverage
uv run pytest tests/ --cov=src --cov-report=html --ignore=tests/legacy_tests
```

### Test Coverage

- ✅ BaseDocumentProcessor interface
- ✅ ProcessorRegistry met parallel classification
- ✅ InvoiceProcessor (classificatie, extractie, validatie, merging, metrics)
- ✅ CVProcessor (classificatie, extractie, validatie, merging, metrics)
- ✅ Statistics tracking
- ✅ Utilities (chunking, PDF extraction)

---

## 🔌 Nieuw Documenttype Toevoegen

Simpel 3-stappen proces - **geen server wijzigingen nodig!**

### 1. Maak Processor Module

```bash
mkdir -p src/mcp_invoice_processor/processors/receipt
```

### 2. Implementeer Processor

```python
# processors/receipt/processor.py
from ..base import BaseDocumentProcessor
from .models import ReceiptData

class ReceiptProcessor(BaseDocumentProcessor):
    @property
    def document_type(self) -> str:
        return "receipt"
    
    @property
    def display_name(self) -> str:
        return "Kassabon"
    
    @property
    def tool_name(self) -> str:
        return "process_receipt"
    
    @property
    def tool_description(self) -> str:
        return "Verwerk kassabon documenten en extraheer gestructureerde data"
    
    @property
    def tool_examples(self) -> Dict[str, Any]:
        return {
            "emoji": "🧾",
            "example_text": "Kassabon\nDatum: 2024-01-15\nTotaal: €25.50",
            "extracted_fields": ["Datum", "Totaal bedrag", "Winkel"],
            "usage_example": "result = await process_receipt(text, 'hybrid')",
            "keywords": ["bon", "kassabon", "receipt", "pinbetaling"],
            "supported_methods": ["hybrid", "json_schema", "prompt_parsing"],
            "supported_formats": [".txt", ".pdf"]
        }
    
    @property
    def classification_keywords(self) -> Set[str]:
        return {"bon", "kassabon", "receipt", "pinbetaling", ...}
    
    async def classify(self, text) -> float:
        # Implementeer classificatie
        ...
    
    async def extract(self, text, method) -> Optional[ReceiptData]:
        # Implementeer extractie
        ...
    
    # ... implementeer overige methods
```

### 3. Registreer

```python
# processors/__init__.py
from .receipt import ReceiptProcessor

def _init_processors():
    # ... bestaande registraties
    registry.register(ReceiptProcessor())
```

**Klaar!** De processor is nu automatisch beschikbaar via:
- ✅ **Dynamische MCP Tool**: `process_receipt` wordt automatisch geregistreerd
- ✅ **Automatische Classificatie**: In registry classificatie
- ✅ **Dynamische Documentatie**: Voorbeelden verschijnen in `mcp://document-types`
- ✅ **MCP Resources**: `stats://receipt`, `schema://receipt`, etc.
- ✅ **Geen server wijzigingen**: FastMCP server blijft volledig generiek

---

## 📁 Project Structuur

```
cursor_ratsenbergertest/
├── src/mcp_invoice_processor/
│   ├── processors/              # ✨ MODULAIRE PROCESSORS
│   │   ├── base.py              # BaseDocumentProcessor interface
│   │   ├── registry.py          # ProcessorRegistry + Resources
│   │   ├── invoice/             # Invoice processor module
│   │   └── cv/                  # CV processor module
│   │
│   ├── processing/              # 🔧 UTILITIES
│   │   ├── chunking.py          # Text chunking
│   │   └── text_extractor.py   # PDF extraction
│   │
│   ├── monitoring/              # 📊 METRICS & MONITORING
│   │   ├── metrics.py           # Metrics collection
│   │   └── dashboard.py         # Web dashboard
│   │
│   ├── tools.py                 # MCP tool functions
│   ├── fastmcp_server.py        # FastMCP server
│   ├── http_server.py           # HTTP server
│   ├── config.py                # Configuration
│   └── logging_config.py        # Logging setup
│
├── tests/
│   ├── test_processors.py       # ✅ Nieuwe processor tests
│   ├── test_pipeline.py         # ✅ Updated tests
│   ├── TEST_MIGRATION_GUIDE.md  # Migration guide
│   └── legacy_tests/            # 📁 Gearchiveerde oude tests
│
├── REFACTORING_PLAN.md          # Complete design document
├── REFACTORING_SUMMARY.md       # Refactoring resultaten
├── pyproject.toml               # Dependencies
└── README.md                    # Deze file
```

---

## 🔄 Extractie Methoden

### Hybrid (Aanbevolen) ⭐
```python
result = await processor.extract(text, ctx, method="hybrid")
```
- Probeert JSON schema eerst
- Fallback naar prompt parsing bij lage quality
- Beste balance tussen precisie en flexibiliteit

### JSON Schema
```python
result = await processor.extract(text, ctx, method="json_schema")
```
- Structured outputs via Ollama
- Hoge precisie
- Ideaal voor gestructureerde documenten

### Prompt Parsing
```python
result = await processor.extract(text, ctx, method="prompt_parsing")
```
- Traditionele LLM met JSON parsing
- Flexibel voor complexe documenten
- Automatic JSON repair

---

## 📊 Monitoring Dashboard

```bash
# Start monitoring dashboard
uv run python -m mcp_invoice_processor.monitoring.dashboard

# Open browser: http://localhost:8000
```

**Features:**
- Realtime metrics met auto-refresh
- Document processing statistics
- Ollama integration metrics
- System health status
- Per-processor breakdown

---

## 🤖 Ollama Setup

```bash
# Download model
ollama pull llama3.2

# Of gebruik ander model
ollama pull mistral

# Update config
export OLLAMA_MODEL=mistral
```

**Aanbevolen Models:**
- `llama3.2` (default) - Uitstekende balance
- `mistral` - Sneller, goed voor facturen
- `llama3.2:70b` - Hoogste kwaliteit (requires meer resources)

---

## 🔒 Configuratie

Via environment variables of `.env` file:

```bash
# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TIMEOUT=120

# Logging
LOG_LEVEL=INFO
```

---

## 🐳 Docker Deployment

```bash
# Build
docker build -t mcp-document-processor .

# Run
docker run -d \
  --name mcp-processor \
  -p 8080:8080 \
  -e OLLAMA_HOST="http://host.docker.internal:11434" \
  mcp-document-processor
```

---

## 📚 Documentatie

- **[REFACTORING_PLAN.md](REFACTORING_PLAN.md)** - Complete design document met FastMCP best practices
- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Refactoring resultaten en metrics
- **[MCP_TOOLS_DOCUMENTATION.md](MCP_TOOLS_DOCUMENTATION.md)** - Uitgebreide tool documentatie
- **[tests/TEST_MIGRATION_GUIDE.md](tests/TEST_MIGRATION_GUIDE.md)** - Test migration guide

### FastMCP References
- [Context](https://gofastmcp.com/servers/context) - Logging en progress
- [Resources](https://gofastmcp.com/servers/resources) - Data exposure
- [Tools](https://gofastmcp.com/servers/tools) - Tool annotations
- [Progress](https://gofastmcp.com/servers/progress) - Progress reporting

---

## 🎨 Code Voorbeelden

### Nieuwe Processor Toevoegen

```python
from processors.base import BaseDocumentProcessor
from processors import register_processor

class ReceiptProcessor(BaseDocumentProcessor):
    @property
    def document_type(self) -> str:
        return "receipt"
    
    @property
    def display_name(self) -> str:
        return "Kassabon"
    
    @property
    def classification_keywords(self) -> Set[str]:
        return {"bon", "kassabon", "receipt", "pinbetaling"}
    
    async def classify(self, text, ctx) -> float:
        text_lower = text.lower()
        matches = sum(1 for kw in self.classification_keywords if kw in text_lower)
        return min(matches * 10.0, 100.0)
    
    async def extract(self, text, ctx, method) -> Optional[ReceiptData]:
        # Implementeer extractie logica
        ...
    
    # ... implement alle abstracte methods

# Registreer
register_processor(ReceiptProcessor())
```

### Document Verwerken

```python
from mcp_invoice_processor.processors import get_registry
from fastmcp import Context

async def process_document(text: str, ctx: Context):
    # Get registry
    registry = get_registry()
    
    # Classificeer (parallel over alle processors!)
    doc_type, confidence, processor = await registry.classify_document(text, ctx)
    
    if processor:
        # Extraheer data
        data = await processor.extract(text, ctx, method="hybrid")
        
        # Get custom metrics
        metrics = await processor.get_custom_metrics(data, ctx)
        
        return {
            "type": doc_type,
            "confidence": confidence,
            "data": data.model_dump(),
            "metrics": metrics
        }
```

### Statistics Ophalen

```python
from mcp_invoice_processor.processors import get_registry

registry = get_registry()

# Per processor
invoice_stats = registry.get_processor("invoice").get_statistics()
cv_stats = registry.get_processor("cv").get_statistics()

# Global
global_stats = registry.get_all_statistics()

print(f"Total processed: {global_stats['global']['total_documents_processed']}")
print(f"Success rate: {global_stats['global']['global_success_rate']}%")
```

---

## 🧪 Testing

### Run Tests

```bash
# Nieuwe processor tests
uv run pytest tests/test_processors.py -v

# Pipeline tests  
uv run pytest tests/test_pipeline.py -v

# Alle moderne tests
uv run pytest tests/ --ignore=tests/legacy_tests -v

# Met coverage report
uv run pytest tests/ --cov=src --cov-report=html --ignore=tests/legacy_tests
```

### Test Data

Test documenten in `test_documents/`:
- `sample_invoice.txt` - Voorbeeld factuur
- `sample_cv.txt` - Voorbeeld CV

---

## 📈 Performance

### Real-World Performance Metrics

**PDF Document Processing:**
```
CV PDF (martin-ingescande-CV-losvanbrief-sikkieversie5.pdf):
- Processing Time: 17.71s
- Confidence: 70%
- Data Extracted: 8 jobs, 4 education, 12 skills

Invoice PDF (amazon_rugtas-factuur.pdf):
- Processing Time: 5.07s  
- Confidence: 100%
- Data Extracted: Complete financial data
```

**Text Document Processing:**
```
Invoice Text: ~3s processing time
CV Text: ~3s processing time
Confidence: 50-90% depending on content
```

### Classificatie Speed

**Oude Architecture** (Sequential):
```
Invoice check: 0.1ms
CV check: 0.1ms
Total: 0.2ms (sequential)
```

**Nieuwe Architecture** (Parallel):
```
All processors parallel: max(0.1ms) = 0.1ms
Speedup: 2× (schaalt met aantal processors!)
```

### Memory Efficient

- Processors delen geen state
- Lazy loading van models
- Efficient chunk processing
- PDF text extraction optimized

---

## 🎁 Voordelen

### Modulariteit
✅ Elk type volledig zelfstandig  
✅ Easy testing in isolation  
✅ Bug fixes blijven lokaal  

### Performance
⚡ Parallel classification  
⚡ Async non-blocking I/O  
⚡ Scalable design  

### Observability
📊 Realtime statistics  
📝 Structured logging  
📈 Progress reporting  

### Extensibility
🔌 Plugin architecture  
🔌 Nieuw type = nieuwe folder  
🔌 Zero changes in existing code  

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-processor`
3. Implement your processor in `processors/yourtype/`
4. Add tests in `tests/test_yourtype.py`
5. Commit: `git commit -m 'feat(processors): add YourType processor'`
6. Push: `git push origin feature/new-processor`
7. Create Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

- [FastMCP](https://github.com/fastmcp/fastmcp) - Modern MCP server framework
- [Ollama](https://ollama.ai/) - Local LLM server
- [PyMuPDF](https://pymupdf.readthedocs.io/) - Fast PDF processing
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager

---

## 🎯 Version

**Current Version**: 2.1.0  
**Architecture**: Volledig Generieke Modular Processor System  
**Status**: Production Ready ✅
