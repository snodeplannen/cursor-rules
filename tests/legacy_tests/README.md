# Legacy Tests

Deze tests gebruiken de oude processing module architecture en zijn gearchiveerd.

## 📋 Status

**Gearchiveerde Tests**: 19 files  
**Reden**: Gebruiken oude imports van verwijderde modules (classification.py, pipeline.py, merging.py)

## 🔄 Migratie

Deze tests kunnen gemigreerd worden naar de nieuwe processor architecture met behulp van de `TEST_MIGRATION_GUIDE.md` in de parent directory.

## ✅ Moderne Tests

Gebruik in plaats daarvan de nieuwe test suite:
- `../test_processors.py` - Complete processor architecture tests
- `../test_pipeline.py` - Updated pipeline tests met nieuwe architecture

## 📝 Legacy Test Files

1. `test_amazon_factuur.py` - Amazon factuur test
2. `test_comprehensive_comparison.py` - Extractie methode vergelijking
3. `test_debug_json_schema.py` - JSON schema debugging
4. `test_error_analysis.py` - Error analysis
5. `test_factuur_tekst.py` - Factuur text processing
6. `test_final_validation.py` - Final validation
7. `test_hybrid_mode.py` - Hybrid mode testing
8. `test_improved_extraction.py` - Improved extraction
9. `test_json_schema_extraction.py` - JSON schema extraction
10. `test_ollama_integration.py` - Ollama integration
11. `test_pipeline_direct.py` - Direct pipeline testing
12. `test_pdf_processing.py` - PDF processing
13. `test_real_documents.py` - Real document processing
14. `test_real_pdf_comparison.py` - PDF comparison
15. `test_all_mcp_commands.py` - MCP commands
16. `test_all_mcp_tools.py` - MCP tools
17. `test_mcp_server.py` - MCP server
18. `test_mcp_tools_detailed.py` - Detailed MCP tools
19. `test_mcp_tools_simple.py` - Simple MCP tools

## 🚫 Waarom Niet Gemigreerd?

Deze tests testen de oude monolithische pipeline architectuur die niet meer bestaat:
- `classification.py` (verwijderd)
- `pipeline.py` (verwijderd)
- `merging.py` (verwijderd)

De nieuwe processor architecture heeft complete test coverage in `test_processors.py`.

## 🗑️ Kan Verwijderd Worden

Deze tests kunnen veilig verwijderd worden zodra je tevreden bent met de nieuwe test suite.

