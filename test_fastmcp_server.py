#!/usr/bin/env python3
"""
Test script voor de FastMCP server met echte document verwerking.
Dit test de server zoals beschreven in de Scrapfly MCP guide.
"""

import asyncio
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_fastmcp_server():
    """Test de FastMCP server functionaliteit."""
    
    print("🚀 Testen FastMCP Server Functionaliteit")
    print("=" * 60)
    
    # Import de server tools
    from src.mcp_invoice_processor.fastmcp_server import (
        process_document_text, 
        process_document_file,
        classify_document_type,
        get_metrics,
        health_check
    )
    
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
    
    # Test 1: Health Check
    print("\n🔍 Test 1: Health Check")
    print("-" * 30)
    
    ctx = TestContext()
    health_result = await health_check(ctx)
    
    print(f"Status: {health_result.get('status', 'unknown')}")
    print(f"Ollama Status: {health_result.get('ollama_status', 'unknown')}")
    if 'available_models' in health_result:
        print(f"Available Models: {len(health_result['available_models'])}")
    
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
        result = await classify_document_type(test_text, ctx)
        print(f"{test_name}: {result.get('document_type', 'unknown')} (confidence: {result.get('confidence', 'unknown')})")
    
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
        invoice_result = await asyncio.wait_for(
            process_document_text(invoice_text, ctx),
            timeout=120.0  # 2 minuten timeout voor Ollama
        )
        
        if 'error' not in invoice_result:
            print("✅ Factuur succesvol verwerkt")
            print(f"   Document type: {invoice_result.get('document_type', 'unknown')}")
            print(f"   Processing time: {invoice_result.get('processing_time', 0):.2f}s")
            
            # Toon enkele geëxtraheerde velden
            if 'invoice_number' in invoice_result:
                print(f"   Factuurnummer: {invoice_result['invoice_number']}")
            if 'total_amount' in invoice_result:
                print(f"   Totaal bedrag: €{invoice_result['total_amount']}")
            if 'supplier_name' in invoice_result:
                print(f"   Leverancier: {invoice_result['supplier_name']}")
        else:
            print(f"❌ Factuur verwerking mislukt: {invoice_result['error']}")
    
    except asyncio.TimeoutError:
        print("❌ Timeout bij factuur verwerking (120s)")
    except Exception as e:
        print(f"❌ Fout bij factuur verwerking: {e}")
    
    # Test 4: File Processing
    print("\n📁 Test 4: File Processing")
    print("-" * 30)
    
    # Test met de sample bestanden
    test_files = [
        "test_documents/sample_invoice.txt",
        "test_documents/sample_cv.txt"
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            ctx = TestContext()
            try:
                file_result = await asyncio.wait_for(
                    process_document_file(file_path, ctx),
                    timeout=120.0
                )
                
                if 'error' not in file_result:
                    print(f"✅ {file_path} succesvol verwerkt")
                    print(f"   Document type: {file_result.get('document_type', 'unknown')}")
                    print(f"   Processing time: {file_result.get('processing_time', 0):.2f}s")
                else:
                    print(f"❌ {file_path} verwerking mislukt: {file_result['error']}")
            
            except asyncio.TimeoutError:
                print(f"❌ Timeout bij {file_path} verwerking (120s)")
            except Exception as e:
                print(f"❌ Fout bij {file_path} verwerking: {e}")
        else:
            print(f"⚠️  {file_path} niet gevonden")
    
    # Test 5: Metrics
    print("\n📊 Test 5: Metrics")
    print("-" * 30)
    
    ctx = TestContext()
    metrics_result = await get_metrics(ctx)
    
    if 'error' not in metrics_result:
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
    else:
        print(f"❌ Metrics ophalen mislukt: {metrics_result['error']}")
    
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
