# MCP Document Processor - Tools Documentatie v2.0

## 📋 Overzicht

Moderne modulaire document processor met AI-powered extractie via FastMCP en Ollama.

**Versie**: 1.0.0  
**Architecture**: Modular Processor System  
**Transport**: STDIO (Cursor) / HTTP (API)  
**AI Model**: Ollama LLM (default: llama3.2)

---

## 🎯 Processor Architecture

### Modulaire Processors

Elk documenttype heeft een zelfstandige processor:

**InvoiceProcessor** (`processors/invoice/`)
- 📋 29 classificatie keywords
- 💰 Extractie van bedragen, BTW, line items
- 🔄 Hybrid mode (json_schema + prompt_parsing)

**CVProcessor** (`processors/cv/`)
- 👤 17 classificatie keywords  
- 📝 Extractie van ervaring, opleiding, vaardigheden
- 🔄 Hybrid mode voor beste resultaten

### ProcessorRegistry

Centraal beheer met:
- ⚡ **Parallel classificatie** (alle processors tegelijk!)
- 📊 Global statistics aggregatie
- 🔌 Automatische resource registratie

---

## 🔧 MCP Tools

### 1. `process_document_text` ⭐

Verwerk document tekst met automatische type detectie.

**Nieuwe Features v1.0:**
- ✅ Async parallel classificatie
- ✅ Realtime progress updates
- ✅ Confidence scores
- ✅ Processor-specific extraction
- ✅ Per-processor statistics

**Parameters:**
- `text` (str, required): Document tekst
- `ctx` (Context, required): FastMCP context
- `extraction_method` (str, optional): "hybrid" (default), "json_schema", "prompt_parsing"

**Return Structure:**
```json
{
  "document_type": "invoice",
  "confidence": 95.3,
  "processor": "process_invoice",
  "processing_time": 2.14,
  
  // Invoice fields
  "invoice_id": "INV-001",
  "invoice_number": "INV-001",
  "supplier_name": "Bedrijf A",
  "customer_name": "Klant B",
  "subtotal": 100.0,
  "vat_amount": 21.0,
  "total_amount": 121.0,
  "currency": "EUR",
  "line_items": [
    {
      "description": "Product X",
      "quantity": 2,
      "unit_price": 50.0,
      "line_total": 100.0,
      "vat_rate": 21.0,
      "vat_amount": 21.0
    }
  ]
}
```

**Progress Updates:**
```
📊 0%   - Starting classification
📊 10%  - Classification complete
📊 20%  - Starting extraction
📊 90%  - Extraction complete
📊 100% - Done!
```

**Example:**
```python
result = await process_document_text(
    text="FACTUUR #123...",
    ctx=context,
    extraction_method="hybrid"
)
```

---

### 2. `process_document_file`

Verwerk document bestand (PDF, TXT).

**Parameters:**
- `file_path` (str, required): Pad naar document
- `ctx` (Context, required): FastMCP context
- `extraction_method` (str, optional): "hybrid" (default)

**Supported Formats:**
- `.txt` - Plain text
- `.pdf` - PDF documents (automatic text extraction)

**Example:**
```python
result = await process_document_file(
    file_path="factuur.pdf",
    ctx=context,
    extraction_method="hybrid"
)
```

---

### 3. `classify_document_type` 🆕

Classificeer document type met confidence scores (v2.0 feature).

**Nieuwe v1.0 Features:**
- ✅ Parallel classification over alle processors
- ✅ Numeric confidence scores (0-100)
- ✅ Confidence levels (high/medium/low)
- ✅ Processor metadata

**Parameters:**
- `text` (str, required): Document tekst
- `ctx` (Context, required): FastMCP context

**Return Structure:**
```json
{
  "document_type": "invoice",
  "confidence": 87.3,
  "confidence_level": "high",
  "processor": "process_invoice",
  "display_name": "Factuur"
}
```

**Confidence Levels:**
- `high`: confidence >= 70%
- `medium`: confidence >= 40%
- `low`: confidence < 40%
- `none`: no processor match

**Classification Keywords:**

**Invoice** (29 keywords):
- factuur, invoice, totaal, total, bedrag, amount
- btw, vat, klant, customer, leverancier, supplier
- artikel, item, prijs, price, kosten, costs
- betaling, payment, nummer, datum, date
- €, eur, euro, subtotaal, vervaldatum, due

**CV** (17 keywords):
- ervaring, opleiding, vaardigheden, curriculum vitae
- werkervaring, education, experience, skills
- competenties, diploma, werkgever, employer
- functie, position, carrière, career, cv, resume

**Example:**
```python
result = await classify_document_type(
    text="FACTUUR #123\nTotaal: €100",
    ctx=context
)
# Returns: {"document_type": "invoice", "confidence": 90.0, ...}
```

---

### 4. `get_metrics` 📊

Comprehensive metrics van alle processors en system.

**Nieuwe v1.0 Features:**
- ✅ Per-processor statistics
- ✅ Global aggregated statistics
- ✅ Success rates per processor
- ✅ Average confidence scores
- ✅ Average completeness scores

**Parameters:**
- `ctx` (Context, required): FastMCP context

**Return Structure:**
```json
{
  // Global system metrics
  "timestamp": "2025-01-01T12:00:00",
  "system": {
    "uptime": "02:15:30",
    "memory_usage_mb": 153.8,
    "cpu_usage_percent": 27.2
  },
  "ollama": {
    "total_requests": 42,
    "successful_requests": 40,
    "failed_requests": 2,
    "average_response_time": 1.85
  },
  
  // New: Per-processor statistics
  "processors": {
    "total_processors": 2,
    "processor_types": ["invoice", "cv"],
    "processors": {
      "invoice": {
        "total_processed": 25,
        "total_successful": 24,
        "total_failed": 1,
        "success_rate": 96.0,
        "avg_processing_time": 2.1,
        "avg_confidence": 88.5,
        "avg_completeness": 92.3,
        "processor_type": "invoice",
        "display_name": "Factuur"
      },
      "cv": {
        "total_processed": 17,
        "total_successful": 16,
        "total_failed": 1,
        "success_rate": 94.1,
        "avg_processing_time": 2.8,
        "avg_confidence": 85.2,
        "avg_completeness": 89.7,
        "processor_type": "cv",
        "display_name": "Curriculum Vitae"
      }
    },
    "global": {
      "total_documents_processed": 42,
      "total_successful": 40,
      "total_failed": 2,
      "global_success_rate": 95.2
    }
  }
}
```

**Example:**
```python
metrics = await get_metrics(ctx=context)
print(f"Global success rate: {metrics['processors']['global']['global_success_rate']}%")
print(f"Invoice processed: {metrics['processors']['processors']['invoice']['total_processed']}")
```

---

### 5. `health_check` 🏥

System health check met processor info.

**Nieuwe v1.0 Features:**
- ✅ Processor count en types
- ✅ Per-processor statistics
- ✅ Ollama model in use

**Parameters:**
- `ctx` (Context, required): FastMCP context

**Return Structure:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00",
  "ollama": {
    "status": "healthy",
    "available_models": ["llama3.2", "mistral"],
    "model_in_use": "llama3.2"
  },
  "processors": {
    "count": 2,
    "types": ["invoice", "cv"],
    "total_documents_processed": 42,
    "global_success_rate": 95.2
  },
  "system": {
    "uptime": "02:15:30",
    "total_ollama_requests": 45
  }
}
```

**Example:**
```python
health = await health_check(ctx=context)
if health['status'] == 'healthy':
    print("✅ System healthy!")
```

---

## 📊 MCP Resources (v1.0 Nieuw!)

Processors exposen automatisch resources via MCP protocol.

### Per-Processor Resources

**Statistics**: `stats://{processor_type}`
```python
# Invoice stats
stats = await read_resource("stats://invoice")

# CV stats  
stats = await read_resource("stats://cv")
```

**JSON Schema**: `schema://{processor_type}`
```python
# Invoice schema
schema = await read_resource("schema://invoice")

# CV schema
schema = await read_resource("schema://cv")
```

**Keywords**: `keywords://{processor_type}`
```python
# Invoice keywords
keywords = await read_resource("keywords://invoice")
# Returns: {"document_type": "invoice", "keywords": ["factuur", "invoice", ...]}
```

### Global Resources

**All Statistics**: `stats://all`
```python
stats = await read_resource("stats://all")
# Returns aggregated stats van alle processors
```

**Resource Annotations:**
- `readOnlyHint: true` - Resources wijzigen geen data
- `idempotentHint: true` - Herhaald lezen heeft geen side effects
- `mime_type: application/json` - JSON content

---

## 🎯 Extractie Methoden

### Hybrid Mode (Aanbevolen) ⭐

```python
result = await process_document_text(text, ctx, "hybrid")
```

**Workflow:**
1. Probeer JSON schema mode eerst
2. Evalueer completeness (> 90% = accept)
3. Bij lage quality: fallback naar prompt parsing
4. Return beste resultaat

**Beste Voor:**
- Algemeen gebruik
- Onbekende document kwaliteit
- Maximale betrouwbaarheid

### JSON Schema Mode

```python
result = await process_document_text(text, ctx, "json_schema")
```

**Features:**
- Ollama structured outputs
- Hoge precisie
- Consistente output structuur

**Beste Voor:**
- Gestructureerde documenten
- Facturen met vaste format
- Maximale nauwkeurigheid

### Prompt Parsing Mode

```python
result = await process_document_text(text, ctx, "prompt_parsing")
```

**Features:**
- Traditionele LLM prompting
- Flexibele extractie
- Automatic JSON repair

**Beste Voor:**
- Complexe documenten
- Ongestructureerde data
- Maximale flexibiliteit

---

## 📈 Performance Kenmerken

### Parallel Classification

**Oude Architecture** (v1.0):
```
Sequential: Invoice(0.1ms) + CV(0.1ms) = 0.2ms
```

**Nieuwe Architecture** (v1.0):
```
Parallel: max(Invoice, CV) = 0.1ms
Speedup: 2× (schaalt met processors!)
```

### Async I/O

- Non-blocking Ollama requests
- Concurrent document processing
- Scalable met meer processors

### Statistics Tracking

- Realtime updates
- Zero performance overhead
- Rolling averages

---

## 🔍 Logging & Progress

### Structured Logging

Alle processor operations loggen via FastMCP Context met metadata:

```python
await ctx.info(
    "Processing invoice", 
    extra={
        "processor": "invoice",
        "confidence": 95.3,
        "method": "hybrid",
        "text_length": 2048
    }
)
```

**Log Levels:**
- `debug` - Detailed execution info
- `info` - Normal operations
- `warning` - Potential issues
- `error` - Errors en failures

### Progress Reporting

Realtime progress updates tijdens verwerking:

```python
await ctx.report_progress(progress=50.0, total=100.0)
```

**Stages:**
1. Classification (0-20%)
2. Extraction (20-90%)
3. Validation (90-100%)

---

## 📚 Code Voorbeelden

### Basic Usage

```python
from mcp_invoice_processor.tools import process_document_text
from fastmcp import Context

async def process_invoice(text: str, ctx: Context):
    result = await process_document_text(
        text=text,
        ctx=ctx,
        extraction_method="hybrid"
    )
    
    if "error" not in result:
        print(f"Type: {result['document_type']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Total: €{result.get('total_amount', 0)}")
```

### Gebruik Processors Direct

```python
from mcp_invoice_processor.processors import get_registry
from mcp_invoice_processor.processors.invoice import InvoiceProcessor

# Via registry (automatic classification)
registry = get_registry()
doc_type, confidence, processor = await registry.classify_document(text, ctx)

if processor:
    data = await processor.extract(text, ctx, "hybrid")

# Direct processor usage
invoice_processor = InvoiceProcessor()
confidence = await invoice_processor.classify(text, ctx)
if confidence > 70:
    data = await invoice_processor.extract(text, ctx, "hybrid")
```

### Statistics Monitoring

```python
from mcp_invoice_processor.processors import get_registry

registry = get_registry()

# Per-processor stats
invoice_proc = registry.get_processor("invoice")
stats = invoice_proc.get_statistics()
print(f"Invoice success rate: {stats['success_rate']}%")

# Global stats
global_stats = registry.get_all_statistics()
print(f"Total docs: {global_stats['global']['total_documents_processed']}")
```

---

## 🌟 v1.0 Features

### 1. Parallel Classification
Alle processors classificeren tegelijkertijd → sneller!

### 2. Confidence Scores
Numeric scores (0-100) in plaats van enum types.

### 3. MCP Resources
Processor data beschikbaar via Resources:
- `stats://invoice`, `stats://cv`, `stats://all`
- `schema://invoice`, `schema://cv`
- `keywords://invoice`, `keywords://cv`

### 4. Statistics Tracking
Per-processor en global statistics met rolling averages.

### 5. Progress Reporting
Realtime updates via `ctx.report_progress()`.

### 6. Status Streaming
```python
async for status, data in processor.extract_with_status_stream(text, ctx):
    print(f"{status.stage}: {status.progress}%")
```

### 7. Custom Metrics
Processor-specific metrics:

**Invoice:**
```json
{
  "total_amount": 1234.56,
  "line_items_count": 5,
  "has_vat": true,
  "avg_line_item_value": 246.91
}
```

**CV:**
```json
{
  "work_experience_count": 3,
  "education_count": 2,
  "skills_count": 12,
  "estimated_years_experience": 6
}
```

---

## 🔌 Extensibility

### Nieuw Processor Type Toevoegen

Simpel 3-stappen proces:

**1. Create Module:**
```bash
mkdir -p src/mcp_invoice_processor/processors/receipt
```

**2. Implement Processor:**
```python
from processors.base import BaseDocumentProcessor

class ReceiptProcessor(BaseDocumentProcessor):
    @property
    def document_type(self) -> str:
        return "receipt"
    
    # ... implement interface
```

**3. Register:**
```python
from processors import register_processor
from processors.receipt import ReceiptProcessor

register_processor(ReceiptProcessor())
```

**Klaar!** Processor is nu beschikbaar via:
- `process_document_text` (auto-classification)
- `classify_document_type` (parallel classification)
- MCP Resources (`stats://receipt`, `schema://receipt`)

---

## 📖 Referenties

### Documentatie
- [REFACTORING_PLAN.md](REFACTORING_PLAN.md) - Complete architecture design
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Refactoring results
- [tests/TEST_MIGRATION_GUIDE.md](tests/TEST_MIGRATION_GUIDE.md) - Test migration

### FastMCP
- [Context](https://gofastmcp.com/servers/context) - Logging & progress
- [Resources](https://gofastmcp.com/servers/resources) - Data exposure
- [Tools](https://gofastmcp.com/servers/tools) - Tool annotations
- [Progress](https://gofastmcp.com/servers/progress) - Progress reporting

### External
- [Ollama](https://ollama.ai/) - Local LLM server
- [FastMCP](https://github.com/fastmcp/fastmcp) - MCP framework
- [MCP Protocol](https://modelcontextprotocol.io/) - Protocol spec

---

## 🎊 Migration van v0.x → v1.0

### Breaking Changes

**Removed:**
- ❌ `processing/classification.py` - Gebruik `processor.classify()`
- ❌ `processing/pipeline.py` - Gebruik `processor.extract()`
- ❌ `processing/merging.py` - Gebruik `processor.merge_partial_results()`
- ❌ `DocumentType` enum - Gebruik string-based `document_type`

**New:**
- ✅ `processors/` module - Modulaire processor architecture
- ✅ `BaseDocumentProcessor` - Abstract interface
- ✅ `ProcessorRegistry` - Central management
- ✅ Async everywhere
- ✅ FastMCP best practices

### Quick Migration

**Oude Code:**
```python
from processing.classification import classify_document
from processing.pipeline import extract_structured_data

doc_type = classify_document(text)  # Sync
result = await extract_structured_data(text, doc_type, ctx)
```

**Nieuwe Code:**
```python
from processors import get_registry

registry = get_registry()
doc_type, confidence, processor = await registry.classify_document(text, ctx)  # Async!
result = await processor.extract(text, ctx, "hybrid")
```

---

**Document Processor v1.0** - Modular, Async, FastMCP Compliant ✅
