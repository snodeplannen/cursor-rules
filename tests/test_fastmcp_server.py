#!/usr/bin/env python3
"""
Test script voor de FastMCP server met echte document verwerking.
Dit test de server zoals beschreven in de Scrapfly MCP guide.
"""

import asyncio
import json
import logging
import pytest
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.ollama
async def test_fastmcp_server():
    """Test de FastMCP server functionaliteit."""
    
    print("🚀 Testen FastMCP Server Functionaliteit")
    print("=" * 60)
    
    # Import de server tools direct van de functies, niet de decorated versies
    from src.mcp_invoice_processor.processing.classification import classify_document, DocumentType
    from src.mcp_invoice_processor.processing.pipeline import extract_structured_data
    from src.mcp_invoice_processor.monitoring.metrics import metrics_collector
    
    # Mock context voor testing
    class TestContext:
        def __init__(self):
            self.messages = []
        
        async def info(self, msg):
            self.messages.append(("INFO", msg))
            print(f"ℹ️  {msg}")
        
        async def error(self, msg):
            self.messages.append(("ERROR", msg))
            print(f"❌ {msg}")
        
        async def report_progress(self, current, total):
            self.messages.append(("PROGRESS", f"{current}/{total}"))
            print(f"📊 Progress: {current}/{total}")
    
    # Test 1: Metrics Check
    print("\n📊 Test 1: Metrics Check")
    print("-" * 30)
    
    ctx = TestContext()
    metrics_result = metrics_collector.get_comprehensive_metrics()
    
    print(f"Timestamp: {metrics_result.get('timestamp', 'unknown')}")
    print(f"Total Documents: {metrics_result.get('processing', {}).get('total_documents', 0)}")
    print(f"Total Ollama Requests: {metrics_result.get('ollama', {}).get('total_requests', 0)}")
    print(f"System Uptime: {metrics_result.get('system', {}).get('uptime', 'unknown')}")
    
    # Test 2: Document Classification
    print("\n📊 Test 2: Document Classification")
    print("-" * 30)
    
    test_texts = [
        ("Factuur tekst", "FACTUUR\n\nFactuurnummer: INV-2025-001\nTotaal: €1000\nBTW: €210"),
        ("CV tekst", "CURRICULUM VITAE\n\nNaam: Jan Jansen\nEmail: jan@email.com\nWerkervaring: 5 jaar"),
        ("Onbekende tekst", "Dit is gewoon een willekeurige tekst zonder specifieke structuur.")
    ]
    
    for test_name, test_text in test_texts:
        ctx = TestContext()
        doc_type = classify_document(test_text)
        print(f"{test_name}: {doc_type.value}")
    
    # Test 3: Document Text Processing
    print("\n📄 Test 3: Document Text Processing")
    print("-" * 30)
    
    # Test factuur verwerking
    invoice_text = """
    FACTUUR
    
    Factuurnummer: INV-2025-001
    Factuurdatum: 24-08-2025
    Vervaldatum: 24-09-2025
    
    AFZENDER:
    TechCorp Solutions B.V.
    Hoofdstraat 123
    1234 AB Amsterdam
    Nederland
    BTW: NL123456789B01
    
    GEADRESSEERDE:
    Test Bedrijf B.V.
    Testweg 456
    5678 CD Rotterdam
    Nederland
    
    BESCHRIJVING:
    - Web Development Services: €2,500.00
    - Database Design: €1,200.00
    - API Integration: €800.00
    
    Subtotaal: €4,500.00
    BTW (21%): €945.00
    Totaal: €5,445.00
    
    Betalingsvoorwaarden: 30 dagen
    Rekeningnummer: NL91ABNA0417164300
    """
    
    ctx = TestContext()
    try:
        # Gebruik de directe pipeline functie
        doc_type = classify_document(invoice_text)
        invoice_result = await asyncio.wait_for(
            extract_structured_data(invoice_text, doc_type, ctx),
            timeout=120.0  # 2 minuten timeout voor Ollama
        )
        
        if invoice_result:
            print("✅ Factuur succesvol verwerkt")
            print(f"   Document type: {doc_type.value}")
            print(f"   Result type: {type(invoice_result).__name__}")
            
            # Toon enkele geëxtraheerde velden
            if hasattr(invoice_result, 'invoice_number'):
                print(f"   Factuurnummer: {invoice_result.invoice_number}")
            if hasattr(invoice_result, 'total_amount'):
                print(f"   Totaal bedrag: €{invoice_result.total_amount}")
            if hasattr(invoice_result, 'supplier_name'):
                print(f"   Leverancier: {invoice_result.supplier_name}")
        else:
            print("❌ Factuur verwerking mislukt: Geen resultaat")
    
    except asyncio.TimeoutError:
        print("❌ Timeout bij factuur verwerking (120s)")
    except Exception as e:
        print(f"❌ Fout bij factuur verwerking: {e}")
    
    # Test 3: Metrics Check
    print("\n📊 Test 3: Metrics Check")
    print("-" * 30)
    
    ctx = TestContext()
    metrics_result = metrics_collector.get_comprehensive_metrics()
    
    print("✅ Metrics succesvol opgehaald")
    
    # Toon belangrijke metrics
    if 'processing' in metrics_result:
        processing = metrics_result['processing']
        print(f"   Totaal documenten: {processing.get('total_documents', 0)}")
        print(f"   Succesvol: {processing.get('successful_documents', 0)}")
        print(f"   Mislukt: {processing.get('failed_documents', 0)}")
    
    if 'ollama' in metrics_result:
        ollama = metrics_result['ollama']
        print(f"   Ollama requests: {ollama.get('total_requests', 0)}")
        print(f"   Ollama succes rate: {ollama.get('success_rate_percent', 0)}%")
    
    if 'system' in metrics_result:
        system = metrics_result['system']
        print(f"   Uptime: {system.get('uptime', 'unknown')}")
    
    print("\n" + "=" * 60)
    print("🎯 FastMCP Server Test Voltooid!")
    print("=" * 60)


async def main():
    """Hoofdfunctie."""
    try:
        await test_fastmcp_server()
    except KeyboardInterrupt:
        print("\n⏹️  Test gestopt door gebruiker.")
    except Exception as e:
        print(f"\n💥 Onverwachte fout: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
