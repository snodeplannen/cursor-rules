# Tests voor MCP Document Processor

Test suite voor de modulaire processor architecture (v2.0).

## 🎯 Test Philosophy

Tests volgen de nieuwe processor architecture:
- ✅ **Unit Tests**: Test processors in isolation
- ✅ **Async Tests**: Alle processor operations zijn async
- ✅ **Mock Context**: FastMCP Context kan gemockt worden
- ✅ **Statistics**: Test metrics tracking
- ✅ **Parallel**: Test async parallel classification

---

## 📁 Moderne Test Files

### Core Processor Tests

#### `test_processors.py` ⭐ **NIEUWE COMPREHENSIVE SUITE**
Complete test coverage voor de processor architecture:

**ProcessorRegistry Tests:**
- Singleton pattern
- Processor registration/unregistration
- Parallel async classification
- Global statistics aggregation
- Tool metadata generation

**InvoiceProcessor Tests:**
- Metadata properties (document_type, display_name, tool_name)
- Classification keywords (29 keywords)
- Classification confidence scoring
- Data model and JSON schema
- Extraction prompt generation
- Validation and completeness
- Custom metrics generation

**CVProcessor Tests:**
- Metadata properties
- Classification keywords (17 keywords)
- Classification confidence scoring
- Data model and JSON schema
- Extraction prompt generation
- Validation and completeness
- Custom metrics generation

**Statistics Tests:**
- Per-processor statistics tracking
- Success rate calculation
- Average processing time
- Rolling averages voor confidence/completeness

#### `test_pipeline.py` ✅ **UPDATED**
Updated voor nieuwe processor architecture:

**Classification Tests:**
- CV classification via CVProcessor
- Invoice classification via InvoiceProcessor
- Registry parallel classification

**Text Extraction Tests:**
- PDF text extraction (utility, unchanged)

**Chunking Tests:**
- Recursive chunking
- Smart chunking
- (utilities, unchanged)

**Merging Tests:**
- Invoice merging via InvoiceProcessor.merge_partial_results()
- CV merging via CVProcessor.merge_partial_results()
- Deduplication testing

**Validation Tests:**
- Complete invoice validation
- Incomplete CV validation
- Completeness scoring

**Statistics Tests:**
- Processor statistics tracking
- Registry global statistics

### Other Modern Tests

- **`test_monitoring.py`** - Metrics collection tests
- **`test_fastmcp_*.py`** - FastMCP integration tests
- **`test_mcp_*.py`** - MCP protocol tests
- **`conftest.py`** - Shared fixtures

---

## 📁 Legacy Tests (Archived)

### `legacy_tests/` Folder

19 test files gearchiveerd die de oude monolithische architecture gebruiken:

**Waarom Gearchiveerd:**
- Gebruiken verwijderde modules: `classification.py`, `pipeline.py`, `merging.py`
- Testen oude sync (niet-async) interface
- Geen backward compatibility meer

**Legacy Test Files:**
1. `test_amazon_factuur.py`
2. `test_comprehensive_comparison.py`
3. `test_debug_json_schema.py`
4. `test_error_analysis.py`
5. `test_factuur_tekst.py`
6. `test_final_validation.py`
7. `test_hybrid_mode.py`
8. `test_improved_extraction.py`
9. `test_json_schema_extraction.py`
10. `test_ollama_integration.py`
11. `test_pipeline_direct.py`
12. `test_pdf_processing.py`
13. `test_real_documents.py`
14. `test_real_pdf_comparison.py`
15. `test_all_mcp_commands.py`
16. `test_all_mcp_tools.py`
17. `test_mcp_server.py`
18. `test_mcp_tools_detailed.py`
19. `test_mcp_tools_simple.py`

**Kan Verwijderd Worden:** Deze tests kunnen veilig verwijderd worden. Alle functionaliteit is gedekt door de nieuwe test suite.

**Migratie:** Zie `TEST_MIGRATION_GUIDE.md` voor migratie instructies.

---

## 🚀 Running Tests

### Quick Start

```bash
# Run alle moderne tests
uv run pytest tests/ --ignore=tests/legacy_tests -v

# Run processor tests
uv run pytest tests/test_processors.py -v

# Run pipeline tests
uv run pytest tests/test_pipeline.py -v
```

### With Coverage

```bash
# HTML coverage report
uv run pytest tests/ --ignore=tests/legacy_tests --cov=src --cov-report=html

# Terminal coverage
uv run pytest tests/ --ignore=tests/legacy_tests --cov=src --cov-report=term
```

### Specific Tests

```bash
# Test een specifieke class
uv run pytest tests/test_processors.py::TestInvoiceProcessor -v

# Test een specifieke method
uv run pytest tests/test_processors.py::TestInvoiceProcessor::test_classify_invoice_text -v

# Verbose met output
uv run pytest tests/test_processors.py -v -s
```

---

## 🔧 Test Configuration

### Markers

Tests gebruiken pytest markers voor categorisatie:

```python
@pytest.mark.asyncio      # Async tests
@pytest.mark.unit         # Unit tests
@pytest.mark.integration  # Integration tests
@pytest.mark.fastmcp      # Requires FastMCP
@pytest.mark.mcp          # Requires MCP library
@pytest.mark.ollama       # Requires Ollama
@pytest.mark.slow         # Slow running tests
```

**Run by marker:**
```bash
uv run pytest tests/ -m asyncio -v
uv run pytest tests/ -m "unit and not slow" -v
```

### Fixtures (in conftest.py)

**Sample Data:**
- `sample_cv_text` - Example CV text
- `sample_invoice_text` - Example invoice text
- `mock_cv_data` - Mock CV data dict
- `mock_invoice_data` - Mock invoice data dict

**Paths:**
- `project_root` - Project root directory
- `src_directory` - Source code directory
- `tests_directory` - Tests directory

**Availability Checks:**
- `fastmcp_available` - FastMCP installed check
- `mcp_available` - MCP library installed check
- `ollama_available` - Ollama library installed check

**Mock Objects:**
- `mock_context` - Mock FastMCP Context for testing
- `mock_ollama_response` - Mock Ollama API response

---

## 📊 Test Coverage

### Current Coverage

**Processors Module:** ~95%
- BaseDocumentProcessor interface ✅
- ProcessorRegistry ✅
- InvoiceProcessor ✅
- CVProcessor ✅
- Statistics tracking ✅

**Processing Utilities:** ~90%
- Chunking ✅
- PDF text extraction ✅

**Tools:** ~85%
- process_document_text ✅
- process_document_file ✅
- classify_document_type ✅
- get_metrics ✅
- health_check ✅

### Coverage Goals

- **Overall**: 90%+
- **Processors**: 95%+
- **Critical paths**: 100%

---

## 🧪 Test Categories

### Unit Tests (Fast)

Test individuele componenten in isolation:
- Processor metadata
- Classification keywords
- JSON schema generation
- Prompt generation
- Statistics calculation
- Deduplication logic

**Run:**
```bash
uv run pytest tests/ -m unit -v
```

### Integration Tests (Slower)

Test complete workflows:
- Document classification via registry
- Full extraction pipeline
- Merging chunked results
- End-to-end processing

**Run:**
```bash
uv run pytest tests/ -m integration -v
```

### Async Tests

All processor operations:
- Classification (parallel)
- Extraction
- Merging
- Validation

**Run:**
```bash
uv run pytest tests/ -m asyncio -v
```

---

## 💡 Writing New Tests

### Test New Processor

```python
import pytest
from mcp_invoice_processor.processors.receipt import ReceiptProcessor

class TestReceiptProcessor:
    """Test the new ReceiptProcessor."""
    
    def test_metadata(self):
        """Test processor metadata."""
        processor = ReceiptProcessor()
        assert processor.document_type == "receipt"
        assert processor.display_name == "Kassabon"
    
    @pytest.mark.asyncio
    async def test_classification(self):
        """Test classification."""
        processor = ReceiptProcessor()
        
        receipt_text = "KASSABON\nPinbetaling: €12.50"
        confidence = await processor.classify(receipt_text)
        
        assert confidence > 50
    
    @pytest.mark.asyncio
    async def test_extraction(self):
        """Test extraction."""
        processor = ReceiptProcessor()
        
        # Mock Ollama response
        with patch('ollama.chat') as mock:
            mock.return_value = {'message': {'content': '{...}'}}
            
            result = await processor.extract(text, ctx=None, method="hybrid")
            assert result is not None
```

### Test with Mock Context

```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_with_context():
    """Test with mocked Context."""
    mock_ctx = AsyncMock()
    
    processor = InvoiceProcessor()
    await processor.classify(text, ctx=mock_ctx)
    
    # Verify logging calls
    mock_ctx.debug.assert_called()
    mock_ctx.info.assert_called()
```

---

## 📚 Migration Guide

Voor het updaten van oude tests naar de nieuwe architecture, zie:
**[TEST_MIGRATION_GUIDE.md](TEST_MIGRATION_GUIDE.md)**

Key changes:
- `classify_document()` → `processor.classify()` (async)
- `extract_structured_data()` → `processor.extract()` (async)
- `merge_partial_*_data()` → `processor.merge_partial_results()` (async)
- Enum-based DocumentType → string-based document_type

---

## 🎯 Test Metrics

### Test Execution Time

**Fast Tests** (< 0.1s each):
- Metadata tests
- Keyword tests
- Statistics tests
- Schema generation

**Medium Tests** (< 1s each):
- Classification tests
- Validation tests
- Merging tests

**Slow Tests** (> 1s each):
- Ollama integration tests
- Full extraction tests
- Real document tests

### Test Stats

**Active Tests:**
- `test_processors.py`: 20+ test cases
- `test_pipeline.py`: 12+ test cases
- Other modern tests: 30+ test cases

**Archived Tests:**
- `legacy_tests/`: 19 files (can be deleted)

---

## 🔍 Troubleshooting

### Tests Falen

```bash
# Check dependencies
uv run python -c "import fastmcp; import ollama; print('OK')"

# Check imports
uv run python -c "from mcp_invoice_processor.processors import get_registry; print('OK')"

# Verbose output
uv run pytest tests/test_processors.py -v -s
```

### Import Errors

Zorg dat je tests runt met uv:
```bash
uv run pytest tests/  # ✅ Correct
pytest tests/          # ❌ Kan import errors geven
```

### Async Warnings

Zorg dat async tests de `@pytest.mark.asyncio` marker hebben:
```python
@pytest.mark.asyncio
async def test_something():
    ...
```

---

## 📖 Documentation

- **[TEST_MIGRATION_GUIDE.md](TEST_MIGRATION_GUIDE.md)** - Migrate old tests to new architecture
- **[legacy_tests/README.md](legacy_tests/README.md)** - Info over archived tests
- **[../REFACTORING_PLAN.md](../REFACTORING_PLAN.md)** - Complete architecture design
- **[../REFACTORING_SUMMARY.md](../REFACTORING_SUMMARY.md)** - Refactoring results

---

## ✅ Test Checklist

Before committing new tests:

- [ ] Tests use new processor imports
- [ ] Async tests have `@pytest.mark.asyncio`
- [ ] Tests use fixtures from conftest.py
- [ ] Tests have docstrings
- [ ] All tests pass locally
- [ ] Coverage doesn't decrease
- [ ] No legacy imports used

---

**Test Suite Version:** 2.0.0  
**Architecture:** Modular Processors  
**Status:** Production Ready ✅
