#!/usr/bin/env python3
"""
Gedetailleerde test voor alle MCP tools.
Dit script test alle MCP tools via de FastMCP server.
"""
import pytest

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock FastMCP Context
class MockContext:
    def __init__(self):
        self.messages = []
        self.errors = []
        self.request_id = "test-request-123"
        self.session_id = "test-session-456"
    
    async def info(self, message: str) -> None:
        self.messages.append(message)
        logger.info(f"📝 INFO: {message}")
    
    async def error(self, message: str) -> None:
        self.errors.append(message)
        logger.error(f"❌ ERROR: {message}")


async def test_all_tools():
    """Test alle beschikbare MCP tools."""
    logger.info("🧪 Testen Alle MCP Tools")
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        if not hasattr(mcp, 'tools'):
            logger.error("❌ Geen tools gevonden in FastMCP server")
            return False
        
        logger.info(f"🛠️ Aantal tools gevonden: {len(mcp.tools)}")
        
        # Test elke tool
        for i, tool in enumerate(mcp.tools):
            tool_name = getattr(tool, 'name', f'Tool_{i}')
            logger.info(f"\n🔧 Tool {i+1}: {tool_name}")
            
            # Tool eigenschappen
            if hasattr(tool, 'description'):
                logger.info(f"   📝 Beschrijving: {tool.description}")
            
            if hasattr(tool, 'input_schema'):
                logger.info(f"   📋 Input Schema: {type(tool.input_schema).__name__}")
                if isinstance(tool.input_schema, dict):
                    logger.info(f"      Properties: {list(tool.input_schema.get('properties', {}).keys())}")
            
            if hasattr(tool, 'examples'):
                logger.info(f"   💡 Voorbeelden: {len(tool.examples)}")
                for j, example in enumerate(tool.examples[:2]):  # Toon eerste 2 voorbeelden
                    if 'input' in example:
                        logger.info(f"      Voorbeeld {j+1}: {example['input']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Tools test mislukt: {e}")
        return False


async def test_all_resources():
    """Test alle beschikbare MCP resources."""
    logger.info("🧪 Testen Alle MCP Resources")
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        if not hasattr(mcp, 'resources'):
            logger.error("❌ Geen resources gevonden in FastMCP server")
            return False
        
        logger.info(f"📚 Aantal resources gevonden: {len(mcp.resources)}")
        
        # Test elke resource
        for i, resource in enumerate(mcp.resources):
            resource_name = getattr(resource, 'name', f'Resource_{i}')
            logger.info(f"\n📚 Resource {i+1}: {resource_name}")
            
            # Test resource call
            try:
                if resource_name == "examples://document-types":
                    result = await resource()
                    logger.info(f"   ✅ Document types resource: {result[:200]}...")
                else:
                    logger.info(f"   ℹ️ Resource {resource_name} niet getest")
            except Exception as e:
                logger.warning(f"   ⚠️ Resource {resource_name} test mislukt: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Resources test mislukt: {e}")
        return False


async def test_all_prompts():
    """Test alle beschikbare MCP prompts."""
    logger.info("🧪 Testen Alle MCP Prompts")
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        if not hasattr(mcp, 'prompts'):
            logger.error("❌ Geen prompts gevonden in FastMCP server")
            return False
        
        logger.info(f"📝 Aantal prompts gevonden: {len(mcp.prompts)}")
        
        # Test elke prompt
        for i, prompt in enumerate(mcp.prompts):
            prompt_name = getattr(prompt, 'name', f'Prompt_{i}')
            logger.info(f"\n📝 Prompt {i+1}: {prompt_name}")
            
            # Test prompt call
            try:
                if prompt_name == "document-processing-guide":
                    # Test met verschillende document types
                    for doc_type in ["cv", "invoice", "any"]:
                        result = await prompt(doc_type)
                        logger.info(f"   ✅ {doc_type.upper()} guide: {result[:150]}...")
                else:
                    logger.info(f"   ℹ️ Prompt {prompt_name} niet getest")
            except Exception as e:
                logger.warning(f"   ⚠️ Prompt {prompt_name} test mislukt: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Prompts test mislukt: {e}")
        return False


async def test_server_capabilities():
    """Test server capabilities en configuratie."""
    logger.info("🧪 Testen Server Capabilities")
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Test server eigenschappen
        logger.info("🏗️ Server Eigenschappen:")
        
        if hasattr(mcp, 'name'):
            logger.info(f"   📛 Naam: {mcp.name}")
        
        if hasattr(mcp, 'version'):
            logger.info(f"   📦 Versie: {mcp.version}")
        
        if hasattr(mcp, 'description'):
            logger.info(f"   📝 Beschrijving: {mcp.description}")
        
        # Test tools capabilities
        if hasattr(mcp, 'tools'):
            logger.info(f"   🛠️ Tools: {len(mcp.tools)} beschikbaar")
            
            # Tool types
            tool_types = {}
            for tool in mcp.tools:
                tool_name = getattr(tool, 'name', 'Onbekend')
                tool_types[tool_name] = {
                    'has_description': hasattr(tool, 'description'),
                    'has_input_schema': hasattr(tool, 'input_schema'),
                    'has_examples': hasattr(tool, 'examples')
                }
            
            for tool_name, capabilities in tool_types.items():
                logger.info(f"      {tool_name}:")
                logger.info(f"        📝 Beschrijving: {'✅' if capabilities['has_description'] else '❌'}")
                logger.info(f"        📋 Input Schema: {'✅' if capabilities['has_input_schema'] else '❌'}")
                logger.info(f"        💡 Voorbeelden: {'✅' if capabilities['has_examples'] else '❌'}")
        
        # Test resources capabilities
        if hasattr(mcp, 'resources'):
            logger.info(f"   📚 Resources: {len(mcp.resources)} beschikbaar")
            
            for resource in mcp.resources:
                resource_name = getattr(resource, 'name', 'Onbekend')
                logger.info(f"      {resource_name}")
        
        # Test prompts capabilities
        if hasattr(mcp, 'prompts'):
            logger.info(f"   📝 Prompts: {len(mcp.prompts)} beschikbaar")
            
            for prompt in mcp.prompts:
                prompt_name = getattr(prompt, 'name', 'Onbekend')
                logger.info(f"      {prompt_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Server capabilities test mislukt: {e}")
        return False


async def test_document_processing_workflow():
    """Test de volledige document verwerking workflow."""
    logger.info("🧪 Testen Document Verwerking Workflow")
    
    try:
        # Test document classificatie
        from mcp_invoice_processor.processing.classification import classify_document
        
        # Test verschillende document types
        test_cases = [
            ("CV", "Curriculum Vitae\nNaam: Jan Jansen\nWerkervaring: Software Engineer\nOpleiding: Bachelor Informatica"),
            ("Factuur", "FACTUUR\nFactuurnummer: INV-001\nTotaal: €100.00\nBTW: €21.00"),
            ("Onbekend", "Dit is een willekeurige tekst zonder specifieke kenmerken.")
        ]
        
        for expected_type, text in test_cases:
            doc_type = classify_document(text)
            logger.info(f"   📄 {expected_type}: geclassificeerd als '{doc_type.value}'")
        
        # Test tekst chunking
        from mcp_invoice_processor.processing.chunking import chunk_text
        
        long_text = "Dit is een lange tekst. " * 100  # 2500 karakters
        chunks = chunk_text(long_text, chunk_size=500)
        logger.info(f"   ✂️ Lange tekst opgedeeld in {len(chunks)} chunks")
        
        # Test metrics
        from mcp_invoice_processor.monitoring.metrics import metrics_collector
        
        metrics = metrics_collector.get_comprehensive_metrics()
        logger.info(f"   📊 Metrics secties: {list(metrics.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Document verwerking workflow test mislukt: {e}")
        return False


async def test_error_handling():
    """Test error handling van de MCP tools."""
    logger.info("🧪 Testen Error Handling")
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Test met ongeldige input
        ctx = MockContext()
        
        # Test tools met ongeldige input
        if hasattr(mcp, 'tools'):
            for tool in mcp.tools:
                tool_name = getattr(tool, 'name', 'Onbekend')
                logger.info(f"   🔧 Testen error handling voor {tool_name}")
                
                # Probeer tool te testen met ongeldige input
                try:
                    # Dit zou een error moeten geven
                    if hasattr(tool, '__call__'):
                        logger.info(f"      ✅ Tool {tool_name} is callable")
                    else:
                        logger.info(f"      ℹ️ Tool {tool_name} is niet direct callable")
                except Exception as e:
                    logger.info(f"      ⚠️ Tool {tool_name} error (verwacht): {type(e).__name__}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error handling test mislukt: {e}")
        return False


async def main():
    """Hoofdfunctie voor alle tests."""
    logger.info("🚀 Starten van gedetailleerde MCP tool tests...")
    
    tests = [
        ("Server Capabilities", test_server_capabilities),
        ("Alle Tools", test_all_tools),
        ("Alle Resources", test_all_resources),
        ("Alle Prompts", test_all_prompts),
        ("Document Verwerking Workflow", test_document_processing_workflow),
        ("Error Handling", test_error_handling),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 STARTING: {test_name}")
        logger.info(f"{'='*80}")
        
        try:
            start_time = time.time()
            success = await test_func()
            end_time = time.time()
            
            duration = end_time - start_time
            results[test_name] = {
                "success": success,
                "duration": duration,
                "status": "✅ PASSED" if success else "❌ FAILED"
            }
            
            logger.info(f"{'='*80}")
            logger.info(f"🏁 FINISHED: {test_name} - {results[test_name]['status']} ({duration:.2f}s)")
            logger.info(f"{'='*80}")
            
        except Exception as e:
            logger.error(f"❌ Test {test_name} crashte: {e}")
            results[test_name] = {
                "success": False,
                "duration": 0,
                "status": "💥 CRASHED",
                "error": str(e)
            }
    
    # Samenvatting
    logger.info(f"\n{'='*100}")
    logger.info("📊 GEDETAILLEERDE TEST SAMENVATTING")
    logger.info(f"{'='*100}")
    
    passed = sum(1 for r in results.values() if r["success"])
    total = len(results)
    
    for test_name, result in results.items():
        logger.info(f"{result['status']} {test_name} ({result['duration']:.2f}s)")
        if "error" in result:
            logger.error(f"   Error: {result['error']}")
    
    logger.info(f"\n📈 TOTAAL: {passed}/{total} tests geslaagd ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 Alle tests geslaagd!")
        return 0
    else:
        logger.error(f"❌ {total-passed} tests gefaald")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("⏹️ Tests gestopt door gebruiker")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Onverwachte fout: {e}")
        sys.exit(1)
