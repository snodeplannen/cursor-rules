# MCP Document Processor

Een moderne, modulaire FastMCP server voor intelligente document verwerking met AI-powered extractie.

## 🚀 Nieuwe Modulaire Architecture (v2.0)

**Volledig gerefactored** naar een plugin-gebaseerde processor architecture met:
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
- **🔌 Extensible**: Eenvoudig nieuwe documenttypes toevoegen

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

### ProcessorRegistry

Centraal management voor:
- Processor registratie
- **Parallel async classificatie** (alle processors tegelijk!)
- Global statistics aggregatie
- MCP Resources automatische registratie

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

## 🚀 Gebruik

### Via MCP Client (Cursor)

Configureer in Cursor settings (`mcp_config_cursor.json`):

```json
{
  "mcpServers": {
    "document-processor": {
      "command": "C:\\ProgramData\\miniforge3\\Scripts\\uv.exe",
      "args": [
        "--directory",
        "C:\\py_cursor-rules\\cursor_ratsenbergertest\\",
        "run",
        "python",
        "-m",
        "mcp_invoice_processor"
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

### `process_document_text`
Verwerk document tekst met automatische type detectie.

**Parameters:**
- `text` (str): Document tekst
- `ctx` (Context): FastMCP context voor logging/progress
- `extraction_method` (str): "hybrid", "json_schema", of "prompt_parsing"

**Returns:**
```json
{
  "document_type": "invoice",
  "confidence": 95.5,
  "processor": "process_invoice",
  "processing_time": 2.34,
  "invoice_id": "INV-001",
  "total_amount": 1234.56,
  ...
}
```

### `process_document_file`
Verwerk document bestand (TXT, PDF).

**Parameters:**
- `file_path` (str): Pad naar document
- `ctx` (Context): FastMCP context
- `extraction_method` (str): Extractie methode

### `classify_document_type`
Classificeer document zonder volledige verwerking.

**Returns:**
```json
{
  "document_type": "invoice",
  "confidence": 87.3,
  "confidence_level": "high",
  "processor": "process_invoice",
  "display_name": "Factuur"
}
```

### `get_metrics`
Comprehensive metrics van alle processors.

**Returns:**
```json
{
  "processors": {
    "invoice": {
      "total_processed": 42,
      "success_rate": 95.2,
      "avg_processing_time": 2.1,
      "avg_confidence": 88.5
    },
    "cv": { ... }
  },
  "global": {
    "total_documents_processed": 87,
    "global_success_rate": 94.3
  }
}
```

### `health_check`
System en Ollama status check.

---

## 📊 MCP Resources

Processors exposen automatisch resources:

```
stats://invoice      → Invoice processor statistics
stats://cv           → CV processor statistics
stats://all          → Global statistics

schema://invoice     → InvoiceData JSON schema
schema://cv          → CVData JSON schema

keywords://invoice   → Invoice classification keywords
keywords://cv        → CV classification keywords
```

**Gebruik via MCP client:**
```python
# LLM kan statistics opvragen
stats = await read_resource("stats://invoice")
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

Simpel 3-stappen proces:

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
    def classification_keywords(self) -> Set[str]:
        return {"bon", "kassabon", "receipt", "pinbetaling", ...}
    
    async def classify(self, text, ctx) -> float:
        # Implementeer classificatie
        ...
    
    async def extract(self, text, ctx, method) -> Optional[ReceiptData]:
        # Implementeer extractie
        ...
    
    # ... implementeer overige methods
```

### 3. Registreer

```python
from processors.receipt import ReceiptProcessor
from processors import register_processor

register_processor(ReceiptProcessor())
```

**Klaar!** De processor is nu beschikbaar via:
- Automatische classificatie in registry
- MCP tools
- MCP resources (`stats://receipt`, `schema://receipt`, etc.)

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

**Current Version**: 2.0.0  
**Architecture**: Modular Processor System  
**Status**: Production Ready ✅
