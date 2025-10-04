#!/usr/bin/env python3
"""
Eenvoudige test voor MCP tools.
Dit script test de MCP tools via de FastMCP server.
"""
import pytest

import asyncio
import json
import logging
import sys
from typing import Any, Dict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock FastMCP Context
class MockContext:
    def __init__(self):
        self.messages = []
        self.errors = []
    
    async def info(self, message: str) -> None:
        self.messages.append(message)
        logger.info(f"📝 INFO: {message}")
    
    async def error(self, message: str) -> None:
        self.errors.append(message)
        logger.error(f"❌ ERROR: {message}")


async def test_fastmcp_server():
    """Test de FastMCP server en tools."""
    logger.info("🧪 Testen FastMCP Server en Tools")
    
    try:
        # Import de FastMCP server
        from mcp_invoice_processor.fastmcp_server import mcp
        
        logger.info(f"✅ FastMCP server geïmporteerd")
        
        # Test server eigenschappen
        if hasattr(mcp, 'tools'):
            logger.info(f"🛠️ Aantal tools: {len(mcp.tools)}")
            
            for i, tool in enumerate(mcp.tools):
                tool_name = getattr(tool, 'name', f'Tool_{i}')
                logger.info(f"   {i+1}. {tool_name}")
                
                if hasattr(tool, 'description'):
                    logger.info(f"      📝 Beschrijving: {tool.description}")
                
                if hasattr(tool, 'input_schema'):
                    logger.info(f"      📋 Input Schema: {type(tool.input_schema).__name__}")
                
                if hasattr(tool, 'examples'):
                    logger.info(f"      💡 Voorbeelden: {len(tool.examples)}")
        
        # Test resources
        if hasattr(mcp, 'resources'):
            logger.info(f"📚 Aantal resources: {len(mcp.resources)}")
            
            for i, resource in enumerate(mcp.resources):
                resource_name = getattr(resource, 'name', f'Resource_{i}')
                logger.info(f"   {i+1}. {resource_name}")
        
        # Test prompts
        if hasattr(mcp, 'prompts'):
            logger.info(f"📝 Aantal prompts: {len(mcp.prompts)}")
            
            for i, prompt in enumerate(mcp.prompts):
                prompt_name = getattr(prompt, 'name', f'Prompt_{i}')
                logger.info(f"   {i+1}. {prompt_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FastMCP server test mislukt: {e}")
        return False


async def test_document_processing():
    """Test document verwerking functionaliteit."""
    logger.info("🧪 Testen Document Verwerking")
    
    try:
        # Test document classificatie
        from mcp_invoice_processor.processing.classification import classify_document
        
        # Test CV tekst
        cv_text = "Curriculum Vitae\nNaam: Jan Jansen\nWerkervaring: Software Engineer"
        doc_type = classify_document(cv_text)
        logger.info(f"✅ CV classificatie: {doc_type.value}")
        
        # Test factuur tekst
        invoice_text = "FACTUUR\nFactuurnummer: INV-001\nTotaal: €100.00"
        doc_type2 = classify_document(invoice_text)
        logger.info(f"✅ Factuur classificatie: {doc_type2.value}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Document verwerking test mislukt: {e}")
        return False


async def test_metrics():
    """Test metrics functionaliteit."""
    logger.info("🧪 Testen Metrics")
    
    try:
        from mcp_invoice_processor.monitoring.metrics import metrics_collector
        
        # Test metrics ophalen
        metrics = metrics_collector.get_comprehensive_metrics()
        logger.info(f"✅ Metrics opgehaald: {len(metrics)} secties")
        
        # Test specifieke metrics
        if 'system' in metrics:
            logger.info(f"   🖥️ System uptime: {metrics['system'].get('uptime', 'Onbekend')}")
        
        if 'processing' in metrics:
            logger.info(f"   📊 Documenten verwerkt: {metrics['processing'].get('total_documents', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Metrics test mislukt: {e}")
        return False


async def test_pipeline():
    """Test de document verwerking pipeline."""
    logger.info("🧪 Testen Pipeline")
    
    try:
        from mcp_invoice_processor.processing.pipeline import extract_structured_data
        from mcp_invoice_processor.processing.classification import DocumentType
        
        # Test CV extractie (zonder Ollama)
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
        
        ctx = MockContext()
        
        # Test alleen classificatie (zonder Ollama)
        doc_type = DocumentType.CV
        logger.info(f"✅ Document type: {doc_type.value}")
        
        # Test pipeline functies
        from mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf
        from mcp_invoice_processor.processing.chunking import chunk_text
        
        # Test chunking
        chunks = chunk_text(cv_text, chunk_size=500)
        logger.info(f"✅ Tekst opgedeeld in {len(chunks)} chunks")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline test mislukt: {e}")
        return False


async def main():
    """Hoofdfunctie voor alle tests."""
    logger.info("🚀 Starten van MCP tool tests...")
    
    tests = [
        ("FastMCP Server", test_fastmcp_server),
        ("Document Verwerking", test_document_processing),
        ("Metrics", test_metrics),
        ("Pipeline", test_pipeline),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 STARTING: {test_name}")
        logger.info(f"{'='*60}")
        
        try:
            start_time = asyncio.get_event_loop().time()
            success = await test_func()
            end_time = asyncio.get_event_loop().time()
            
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
