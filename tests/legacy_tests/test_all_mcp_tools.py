#!/usr/bin/env python3
"""
Test script voor alle MCP tools.
Dit script test alle beschikbare MCP tools in de FastMCP server.
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

# Mock FastMCP Context voor testing
class MockFastMCPContext:
    """Mock context voor FastMCP testing."""
    
    def __init__(self):
        self.messages: list[Dict[str, Any]] = []
        self.errors: list[str] = []
        self.progress_calls: list[Dict[str, Any]] = []
        self.request_id = "test-request-123"
        self.session_id = "test-session-456"
    
    async def info(self, message: str) -> None:
        """Log info bericht."""
        self.messages.append({
            "type": "info", 
            "message": message, 
            "timestamp": time.time()
        })
        logger.info(f"📝 INFO: {message}")
    
    async def error(self, message: str) -> None:
        """Log error bericht."""
        self.errors.append(message)
        logger.error(f"❌ ERROR: {message}")
    
    async def report_progress(self, current: int, total: int, message: str | None = None) -> None:
        """Rapporteer voortgang."""
        self.progress_calls.append({
            "current": current,
            "total": total,
            "message": message,
            "timestamp": time.time()
        })
        logger.info(f"📊 PROGRESS: {current}/{total} - {message or ''}")


async def test_process_document_text():
    """Test de process_document_text tool."""
    logger.info("🧪 Test 1: process_document_text (Tekst verwerking)")
    
    try:
        # Import de functie direct uit de module
        from mcp_invoice_processor.fastmcp_server import process_document_text
        
        # Test CV tekst
        cv_text = """
        Curriculum Vitae
        
        Naam: Jan Jansen
        Email: jan.jansen@email.com
        Telefoon: 06-12345678
        
        Samenvatting: Ervaren software ontwikkelaar met expertise in Python.
        
        Werkervaring:
        - Software Engineer bij TechCorp (2020-2023)
        - Junior Developer bij StartupXYZ (2018-2020)
        
        Opleiding:
        - Bachelor Informatica, Universiteit van Amsterdam (2018)
        
        Vaardigheden: Python, JavaScript, React, Docker
        """
        
        ctx = MockFastMCPContext()
        result = await process_document_text(cv_text, ctx)
        
        logger.info(f"✅ CV verwerking resultaat: {json.dumps(result, indent=2, ensure_ascii=False)}")
        logger.info(f"📊 Context berichten: {len(ctx.messages)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ process_document_text test mislukt: {e}")
        return False


async def test_process_document_file():
    """Test de process_document_file tool."""
    logger.info("🧪 Test 2: process_document_file (Bestand verwerking)")
    
    try:
        # Import de functie direct uit de module
        from mcp_invoice_processor.fastmcp_server import process_document_file
        
        # Test met een bestaand bestand
        test_file = "test_factuur.txt"
        if not Path(test_file).exists():
            # Maak een test bestand aan
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("""
                FACTUUR
                
                Factuurnummer: INV-001
                Datum: 2024-01-15
                Klant: Test Bedrijf BV
                Totaal: €150.00
                BTW: €31.50
                """)
        
        ctx = MockFastMCPContext()
        result = await process_document_file(test_file, ctx)
        
        logger.info(f"✅ Bestand verwerking resultaat: {json.dumps(result, indent=2, ensure_ascii=False)}")
        logger.info(f"📊 Context berichten: {len(ctx.messages)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ process_document_file test mislukt: {e}")
        return False


async def test_classify_document_type():
    """Test de classify_document_type tool."""
    logger.info("🧪 Test 3: classify_document_type (Document classificatie)")
    
    try:
        # Import de functie direct uit de module
        from mcp_invoice_processor.fastmcp_server import classify_document_type
        
        # Test CV classificatie
        cv_text = "Curriculum Vitae\nNaam: Jan Jansen\nWerkervaring: Software Engineer"
        ctx = MockFastMCPContext()
        result = await classify_document_type(cv_text, ctx)
        
        logger.info(f"✅ CV classificatie resultaat: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # Test factuur classificatie
        invoice_text = "FACTUUR\nFactuurnummer: INV-001\nTotaal: €100.00"
        ctx2 = MockFastMCPContext()
        result2 = await classify_document_type(invoice_text, ctx2)
        
        logger.info(f"✅ Factuur classificatie resultaat: {json.dumps(result2, indent=2, ensure_ascii=False)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ classify_document_type test mislukt: {e}")
        return False


async def test_get_metrics():
    """Test de get_metrics tool."""
    logger.info("🧪 Test 4: get_metrics (Performance statistieken)")
    
    try:
        # Import de functie direct uit de module
        from mcp_invoice_processor.fastmcp_server import get_metrics
        
        ctx = MockFastMCPContext()
        result = await get_metrics(ctx)
        
        logger.info(f"✅ Metrics resultaat: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ get_metrics test mislukt: {e}")
        return False


async def test_health_check():
    """Test de health_check tool."""
    logger.info("🧪 Test 5: health_check (Service gezondheid)")
    
    try:
        # Import de functie direct uit de module
        from mcp_invoice_processor.fastmcp_server import health_check
        
        ctx = MockFastMCPContext()
        result = await health_check(ctx)
        
        logger.info(f"✅ Health check resultaat: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ health_check test mislukt: {e}")
        return False


async def test_resources():
    """Test de beschikbare resources."""
    logger.info("🧪 Test 6: Resources (Documentatie en voorbeelden)")
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Test document types resource
        if hasattr(mcp, 'resources'):
            for resource in mcp.resources:
                logger.info(f"📚 Resource: {resource.name if hasattr(resource, 'name') else 'Onbekend'}")
                
                # Test resource call
                try:
                    if resource.name == "examples://document-types":
                        result = await resource()
                        logger.info(f"✅ Document types resource: {result[:200]}...")
                    else:
                        logger.info(f"ℹ️ Resource {resource.name} niet getest")
                except Exception as e:
                    logger.warning(f"⚠️ Resource {resource.name} test mislukt: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Resources test mislukt: {e}")
        return False


async def test_prompts():
    """Test de beschikbare prompts."""
    logger.info("🧪 Test 7: Prompts (Document verwerking gidsen)")
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Test prompts
        if hasattr(mcp, 'prompts'):
            for prompt in mcp.prompts:
                logger.info(f"📝 Prompt: {prompt.name if hasattr(prompt, 'name') else 'Onbekend'}")
                
                # Test prompt call
                try:
                    if prompt.name == "document-processing-guide":
                        result = await prompt("cv")
                        logger.info(f"✅ CV processing guide: {result[:200]}...")
                        
                        result2 = await prompt("invoice")
                        logger.info(f"✅ Invoice processing guide: {result2[:200]}...")
                    else:
                        logger.info(f"ℹ️ Prompt {prompt.name} niet getest")
                except Exception as e:
                    logger.warning(f"⚠️ Prompt {prompt.name} test mislukt: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Prompts test mislukt: {e}")
        return False


async def test_server_info():
    """Test server informatie en configuratie."""
    logger.info("🧪 Test 8: Server Informatie")
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp, mcp_settings
        
        logger.info(f"🏗️ Server naam: {mcp_settings.name}")
        logger.info(f"📦 Server versie: {mcp_settings.version}")
        logger.info(f"📝 Server beschrijving: {mcp_settings.description}")
        logger.info(f"👤 Auteur: {mcp_settings.author}")
        logger.info(f"📧 Contact: {mcp_settings.contact}")
        logger.info(f"📄 Licentie: {mcp_settings.license}")
        logger.info(f"🔧 Capabilities: {mcp_settings.capabilities}")
        
        # Tools informatie
        if hasattr(mcp, 'tools'):
            logger.info(f"🛠️ Aantal tools: {len(mcp.tools)}")
            for i, tool in enumerate(mcp.tools):
                logger.info(f"   {i+1}. {tool.name if hasattr(tool, 'name') else 'Onbekend'}")
                if hasattr(tool, 'description'):
                    logger.info(f"      Beschrijving: {tool.description}")
        
        # Resources informatie
        if hasattr(mcp, 'resources'):
            logger.info(f"📚 Aantal resources: {len(mcp.resources)}")
            for i, resource in enumerate(mcp.resources):
                logger.info(f"   {i+1}. {resource.name if hasattr(resource, 'name') else 'Onbekend'}")
        
        # Prompts informatie
        if hasattr(mcp, 'prompts'):
            logger.info(f"📝 Aantal prompts: {len(mcp.prompts)}")
            for i, prompt in enumerate(mcp.prompts):
                logger.info(f"   {i+1}. {prompt.name if hasattr(prompt, 'name') else 'Onbekend'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Server informatie test mislukt: {e}")
        return False


async def test_tools_direct():
    """Test tools direct via de FastMCP server."""
    logger.info("🧪 Test 9: Tools Direct Testen")
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        if hasattr(mcp, 'tools'):
            logger.info(f"🛠️ Aantal tools gevonden: {len(mcp.tools)}")
            
            for i, tool in enumerate(mcp.tools):
                tool_name = getattr(tool, 'name', f'Tool_{i}')
                logger.info(f"   {i+1}. {tool_name}")
                
                # Test tool properties
                if hasattr(tool, 'description'):
                    logger.info(f"      📝 Beschrijving: {tool.description}")
                
                if hasattr(tool, 'input_schema'):
                    logger.info(f"      📋 Input Schema: {type(tool.input_schema).__name__}")
                
                if hasattr(tool, 'examples'):
                    logger.info(f"      💡 Voorbeelden: {len(tool.examples)}")
                
                # Test tool callability
                if hasattr(tool, '__call__'):
                    logger.info(f"      ✅ Tool is callable")
                else:
                    logger.info(f"      ❌ Tool is niet callable")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Tools direct test mislukt: {e}")
        return False


async def main():
    """Hoofdfunctie voor alle tests."""
    logger.info("🚀 Starten van alle MCP tool tests...")
    
    tests = [
        ("Server Informatie", test_server_info),
        ("Tools Direct Testen", test_tools_direct),
        ("Document Tekst Verwerking", test_process_document_text),
        ("Document Bestand Verwerking", test_process_document_file),
        ("Document Classificatie", test_classify_document_type),
        ("Performance Metrics", test_get_metrics),
        ("Health Check", test_health_check),
        ("Resources", test_resources),
        ("Prompts", test_prompts),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 STARTING: {test_name}")
        logger.info(f"{'='*60}")
        
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
            
            logger.info(f"{'='*60}")
            logger.info(f"🏁 FINISHED: {test_name} - {results[test_name]['status']} ({duration:.2f}s)")
            logger.info(f"{'='*60}")
            
        except Exception as e:
            logger.error(f"❌ Test {test_name} crashte: {e}")
            results[test_name] = {
                "success": False,
                "duration": 0,
                "status": "💥 CRASHED",
                "error": str(e)
            }
    
    # Samenvatting
    logger.info(f"\n{'='*80}")
    logger.info("📊 TEST SAMENVATTING")
    logger.info(f"{'='*80}")
    
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
