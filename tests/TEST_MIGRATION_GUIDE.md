# Test Migration Guide

Guide voor het updaten van tests naar de nieuwe processor architecture.

## 🔄 Belangrijkste Wijzigingen

### Oude Imports → Nieuwe Imports

**Classificatie:**
```python
# ❌ OUD
from mcp_invoice_processor.processing.classification import classify_document, DocumentType
doc_type = classify_document(text)  # Sync

# ✅ NIEUW
from mcp_invoice_processor.processors import get_registry
from mcp_invoice_processor.processors.invoice import InvoiceProcessor

processor = InvoiceProcessor()
confidence = await processor.classify(text, ctx)  # Async met confidence score
```

**Extractie:**
```python
# ❌ OUD
from mcp_invoice_processor.processing.pipeline import extract_structured_data, ExtractionMethod
result = await extract_structured_data(text, doc_type, ctx, ExtractionMethod.HYBRID)

# ✅ NIEUW
from mcp_invoice_processor.processors.invoice import InvoiceProcessor

processor = InvoiceProcessor()
result = await processor.extract(text, ctx, method="hybrid")
```

**Merging:**
```python
# ❌ OUD
from mcp_invoice_processor.processing.merging import merge_partial_invoice_data
merged = merge_partial_invoice_data(partial_results)  # Sync

# ✅ NIEUW
from mcp_invoice_processor.processors.invoice import InvoiceProcessor

processor = InvoiceProcessor()
merged = await processor.merge_partial_results(partial_results, ctx)  # Async
```

**Models:**
```python
# ❌ OUD
from mcp_invoice_processor.processing.models import InvoiceData, CVData

# ✅ NIEUW (processor-specific)
from mcp_invoice_processor.processors.invoice.models import InvoiceData
from mcp_invoice_processor.processors.cv.models import CVData

# ✅ ALTERNATIEF (legacy re-export voor backward compatibility)
from mcp_invoice_processor.processing.models import InvoiceData, CVData
```

## 📝 Test Update Checklist

Voor elke test file die oude imports gebruikt:

- [ ] Update imports naar nieuwe processor modules
- [ ] Verander sync `classify_document()` naar async `processor.classify()`
- [ ] Verander `extract_structured_data()` naar `processor.extract()`
- [ ] Verander `merge_partial_*_data()` naar `processor.merge_partial_results()`
- [ ] Voeg `async/await` toe waar nodig
- [ ] Update assertions voor nieuwe return types
- [ ] Test met `pytest tests/test_*.py -v`

## 🔍 Voorbeelden

### Test Classificatie

```python
import pytest
from mcp_invoice_processor.processors.invoice import InvoiceProcessor

class TestClassification:
    @pytest.mark.asyncio
    async def test_invoice_classification(self):
        processor = InvoiceProcessor()
        
        invoice_text = "FACTUUR #123\nTotaal: €100"
        confidence = await processor.classify(invoice_text)
        
        assert confidence > 50  # Hoge confidence voor invoice
```

### Test Extractie

```python
import pytest
from unittest.mock import AsyncMock, patch
from mcp_invoice_processor.processors.invoice import InvoiceProcessor

class TestExtraction:
    @pytest.mark.asyncio
    async def test_invoice_extraction(self):
        processor = InvoiceProcessor()
        
        # Mock Ollama
        with patch('ollama.chat') as mock_ollama:
            mock_ollama.return_value = {
                'message': {
                    'content': '{"invoice_id": "123", ...}'
                }
            }
            
            result = await processor.extract(
                text="FACTUUR #123",
                ctx=None,  # Of mock Context
                method="json_schema"
            )
            
            assert result is not None
            assert result.invoice_id == "123"
```

### Test Registry (Parallel Classificatie)

```python
import pytest
from mcp_invoice_processor.processors import ProcessorRegistry
from mcp_invoice_processor.processors.invoice import InvoiceProcessor
from mcp_invoice_processor.processors.cv import CVProcessor

class TestRegistry:
    @pytest.mark.asyncio
    async def test_parallel_classification(self):
        registry = ProcessorRegistry()
        registry.register(InvoiceProcessor())
        registry.register(CVProcessor())
        
        doc_type, confidence, processor = await registry.classify_document(
            text="FACTUUR #123",
            ctx=None
        )
        
        assert doc_type == "invoice"
        assert processor.document_type == "invoice"
        assert confidence > 0
```

## 🛠️ Utilities (Geen Wijzigingen)

Deze utilities zijn niet veranderd en kunnen gewoon gebruikt worden:

```python
# ✅ Blijven hetzelfde
from mcp_invoice_processor.processing.chunking import chunk_text, ChunkingMethod
from mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf

chunks = chunk_text(text, method=ChunkingMethod.SMART)
pdf_text = extract_text_from_pdf(pdf_bytes)
```

## 📊 Test Status

### ✅ Updated
- `test_processors.py` - Nieuwe comprehensive processor tests
- `test_pipeline.py` - Updated voor nieuwe architecture

### ⏳ Te Updaten (19 files)
De volgende test files gebruiken nog oude imports en moeten geupdatet worden:
- `test_amazon_factuur.py`
- `test_comprehensive_comparison.py`
- `test_debug_json_schema.py`
- `test_error_analysis.py`
- `test_factuur_tekst.py`
- `test_final_validation.py`
- `test_hybrid_mode.py`
- `test_improved_extraction.py`
- `test_json_schema_extraction.py`
- `test_mcp_server.py`
- `test_mcp_tools_detailed.py`
- `test_mcp_tools_simple.py`
- `test_ollama_integration.py`
- `test_pdf_processing.py`
- `test_pipeline_direct.py`
- `test_real_documents.py`
- `test_real_pdf_comparison.py`
- `test_fastmcp_*` (meerdere files)

## 🚀 Snel Starten

Run de nieuwe tests:
```bash
# Nieuwe processor tests
pytest tests/test_processors.py -v

# Updated pipeline tests  
pytest tests/test_pipeline.py -v

# Alle tests
pytest tests/ -v
```

## 💡 Tips

1. **Async Context**: Veel processor methods accepteren een `Context` parameter. Voor tests kan dit `None` zijn of een mock:
   ```python
   from unittest.mock import AsyncMock
   mock_ctx = AsyncMock()
   ```

2. **Confidence Scores**: Processors returnen nu confidence scores (0-100) in plaats van enum types.

3. **Statistics**: Elke processor tracked eigen statistics. Test met:
   ```python
   stats = processor.get_statistics()
   assert stats["total_processed"] > 0
   ```

4. **Parallel Testing**: Registry classificatie is parallel. Tests moeten async zijn.

5. **Legacy Support**: `processing.models` re-exporteert de nieuwe models voor backward compatibility, maar gebruik bij voorkeur de directe imports.

