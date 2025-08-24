# Tests voor MCP Invoice Processor

Deze directory bevat alle tests voor de MCP Invoice Processor, inclusief unit tests, integratie tests en tests voor FastMCP client integratie.

## 📁 Test Bestanden

### Core Tests
- **`test_pipeline.py`** - Unit tests voor de verwerkingspijplijn
- **`test_monitoring.py`** - Unit tests voor metrics en monitoring
- **`conftest.py`** - Gedeelde fixtures en configuratie

### FastMCP Tests
- **`test_fastmcp_client.py`** - Tests voor FastMCP client integratie in STDIO mode
- **`test_fastmcp_cli.py`** - Tests voor FastMCP CLI functionaliteit
- **`test_fastmcp_server.py`** - Direct FastMCP server tests
- **`test_fastmcp_direct.py`** - Direct core logic tests

### MCP Library Tests
- **`test_mcp_client.py`** - Tests voor MCP library integratie in STDIO mode

### Integration Tests
- **`test_ollama_integration.py`** - Ollama integratie tests met echte LLM
- **`test_real_documents.py`** - Tests met echte document bestanden

### Utility Tests
- **`test_metrics_generation.py`** - Metrics test data generator voor dashboard

### Test Runner
- **`run_tests.py`** - Script om alle tests uit te voeren en rapporten te genereren

## 🚀 Test Uitvoeren

### Alle Tests Uitvoeren
```bash
# Met de test runner
uv run python tests/run_tests.py

# Of direct met pytest
uv run pytest tests/ -v
```

### Specifieke Test Categorieën
```bash
# Alleen unit tests
uv run pytest tests/test_pipeline.py -v

# Alleen FastMCP tests
uv run pytest tests/ -m fastmcp -v

# Alleen MCP library tests
uv run pytest tests/ -m mcp -v

# Alleen integratie tests
uv run pytest tests/ -m integration -v
```

### Test Markers
- **`@pytest.mark.fastmcp`** - Tests die FastMCP vereisen
- **`@pytest.mark.mcp`** - Tests die MCP library vereisen
- **`@pytest.mark.ollama`** - Tests die Ollama vereisen
- **`@pytest.mark.integration`** - Integratie tests
- **`@pytest.mark.unit`** - Unit tests
- **`@pytest.mark.slow`** - Langzaam draaiende tests

## 🔧 Test Configuratie

### Dependencies
Tests controleren automatisch of de benodigde dependencies beschikbaar zijn:
- **FastMCP** - Voor FastMCP client tests
- **MCP Library** - Voor MCP library tests
- **Ollama** - Voor Ollama integratie tests

### Fixtures
Gedeelde fixtures zijn beschikbaar in `conftest.py`:
- **`sample_cv_text`** - Voorbeeld CV tekst
- **`sample_invoice_text`** - Voorbeeld factuur tekst
- **`uv_command`** - UV command voor MCP server
- **`mock_*`** - Mock data voor testing

### Test Omgeving
- Tests voegen automatisch de `src` directory toe aan het Python pad
- Alle tests gebruiken UV voor dependency management
- Timeouts zijn ingesteld voor verschillende test types

## 📊 Test Rapportage

### JUnit XML
```bash
uv run pytest tests/ --junitxml=tests/results.xml
```

### HTML Rapport
```bash
uv run pytest tests/ --html=tests/report.html --self-contained-html
```

### Coverage Rapport
```bash
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term
```

## 🧪 Test Types

### Unit Tests
- Testen individuele functies en klassen
- Gebruiken mocks voor externe dependencies
- Snelle uitvoering

### Integratie Tests
- Testen volledige workflows
- Gebruiken echte MCP server via STDIO
- Langzamere uitvoering

### FastMCP Client Tests
- Testen FastMCP client verbinding
- Testen documentverwerking via FastMCP
- Testen foutafhandeling

### MCP Library Tests
- Testen MCP library verbinding
- Testen documentverwerking via MCP library
- Testen foutafhandeling

## 🔍 Test Debugging

### Verbose Output
```bash
uv run pytest tests/ -v -s
```

### Debug Mode
```bash
uv run pytest tests/ --pdb
```

### Specifieke Test
```bash
uv run pytest tests/test_pipeline.py::TestDocumentClassification::test_cv_classification -v -s
```

## 📋 Test Vereisten

### Runtime Vereisten
- Python 3.10+
- UV package manager
- Alle project dependencies geïnstalleerd

### Test Dependencies
- pytest
- pytest-asyncio
- pytest-html (voor HTML rapporten)
- pytest-cov (voor coverage rapporten)

### Optionele Dependencies
- FastMCP (voor FastMCP tests)
- MCP Library (voor MCP library tests)
- Ollama (voor Ollama integratie tests)

## 🚨 Bekende Problemen

### Timeout Issues
- Sommige tests hebben timeouts ingesteld
- MCP server startup kan langzaam zijn
- Pas timeouts aan indien nodig

### Platform Specifieke Paden
- UV command paden zijn Windows-specifiek
- Pas paden aan voor andere besturingssystemen

### Dependency Issues
- Tests skippen automatisch als dependencies ontbreken
- Installeer ontbrekende dependencies voor volledige test coverage

## 🤝 Bijdragen

### Nieuwe Tests Toevoegen
1. Maak een nieuwe test file in de `tests/` directory
2. Gebruik bestaande fixtures uit `conftest.py`
3. Voeg geschikte markers toe
4. Test lokaal voordat je commit

### Test Fixtures Uitbreiden
1. Voeg nieuwe fixtures toe aan `conftest.py`
2. Documenteer de fixtures
3. Zorg voor backward compatibility

### Test Configuratie Aanpassen
1. Pas `conftest.py` aan voor nieuwe configuratie
2. Update deze README indien nodig
3. Test configuratie lokaal

## 📚 Meer Informatie

- [Pytest Documentatie](https://docs.pytest.org/)
- [FastMCP Documentatie](https://gofastmcp.com/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [UV Documentatie](https://docs.astral.sh/uv/)
