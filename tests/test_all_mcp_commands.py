"""
Test script voor alle MCP Invoice Processor commando's met v2.0 processors.
"""

import asyncio
import os
import pytest

from mcp_invoice_processor.processors import get_registry
from mcp_invoice_processor.monitoring.metrics import metrics_collector
from mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf


@pytest.mark.asyncio
async def test_all_commands(mock_context) -> None:
    """Test alle MCP commando's met v2.0."""
    print("=== MCP Invoice Processor - Alle Commando's Test (v2.0) ===\n")
    
    ctx = mock_context
    registry = get_registry()
    
    # Test 1: Document Type Classificatie
    print("1. 📋 Document Type Classificatie Test")
    print("-" * 50)
    
    test_texts = [
        "FACTUUR\nFactuurnummer: INV-001\nTotaal: €100",
        "CURRICULUM VITAE\nNaam: Jan Jansen\nWerkervaring: 5 jaar",
        "Dit is een willekeurige tekst zonder duidelijke indicatoren"
    ]
    
    for i, text in enumerate(test_texts, 1):
        doc_type, confidence, processor = await registry.classify_document(text, ctx)
        print(f"   Test {i}: {doc_type} ({confidence:.1f}% confidence)")
    
    print()
    
    # Test 2: Document Tekst Verwerking
    print("2. 📄 Document Tekst Verwerking Test")
    print("-" * 50)
    
    invoice_text = """FACTUUR
Factuurnummer: TEST-001
Factuurdatum: 15-03-2025
Leverancier: Test Company BV
Klant: Test Klant
Subtotaal: €100,00
BTW: €21,00
Totaal: €121,00"""
    
    try:
        doc_type, confidence, processor = await registry.classify_document(invoice_text, ctx)
        print(f"   Document type: {doc_type} ({confidence:.1f}%)")
        
        if processor:
            result = await processor.extract(invoice_text, ctx, method="hybrid")
            if result:
                print(f"   ✅ Extractie succesvol!")
                print(f"   Type: {type(result).__name__}")
                if hasattr(result, 'invoice_number'):
                    print(f"   Factuurnummer: {result.invoice_number}")
                if hasattr(result, 'total_amount'):
                    print(f"   Totaalbedrag: €{result.total_amount}")
            else:
                print("   ❌ Extractie mislukt")
        else:
            print("   ❌ Geen processor gevonden")
    except Exception as e:
        print(f"   ❌ Fout: {e}")
    
    print()
    
    # Test 3: PDF Bestand Verwerking
    print("3. 📁 PDF Bestand Verwerking Test")
    print("-" * 50)
    
    pdf_file = "amazon_rugtas-factuur.pdf"
    if os.path.exists(pdf_file):
        try:
            with open(pdf_file, 'rb') as f:
                pdf_bytes = f.read()
            
            text = extract_text_from_pdf(pdf_bytes)
            doc_type, confidence, processor = await registry.classify_document(text, ctx)
            print(f"   PDF bestand: {pdf_file}")
            print(f"   Document type: {doc_type} ({confidence:.1f}%)")
            print(f"   Tekst lengte: {len(text)} karakters")
            
            if processor:
                result = await processor.extract(text, ctx, method="hybrid")
                if result:
                    print(f"   ✅ PDF extractie succesvol!")
                    if hasattr(result, 'invoice_number'):
                        print(f"   Factuurnummer: {result.invoice_number}")
                    if hasattr(result, 'supplier_name'):
                        print(f"   Leverancier: {result.supplier_name}")
                else:
                    print("   ❌ PDF extractie mislukt")
        except Exception as e:
            print(f"   ❌ PDF fout: {e}")
    else:
        print(f"   ⚠️ PDF bestand niet gevonden: {pdf_file}")
        pytest.skip(f"PDF bestand niet gevonden: {pdf_file}")
    
    print()
    
    # Test 4: Metrics Opvragen
    print("4. 📊 Metrics Opvragen Test")
    print("-" * 50)
    
    try:
        # Simuleer activiteit
        metrics_collector.record_document_processing("invoice", True, 2.5)
        metrics_collector.record_ollama_request("llama3.2", 1.2, True)
        
        # Haal metrics op
        metrics = metrics_collector.get_comprehensive_metrics()
        print(f"   ✅ Metrics opgehaald")
        print(f"   Totaal documenten: {metrics['processing']['total_documents']}")
        print(f"   Ollama requests: {metrics['ollama']['total_requests']}")
        
        # Processor statistics
        processor_stats = registry.get_all_statistics()
        print(f"   Processors: {processor_stats['total_processors']}")
        print(f"   Types: {processor_stats['processor_types']}")
        
    except Exception as e:
        print(f"   ❌ Metrics fout: {e}")
    
    print("\n=== Alle Tests Voltooid ===")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

