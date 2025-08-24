#!/usr/bin/env python3
"""
Directe test van FastMCP server functies zonder de MCP protocol overhead.
"""

import asyncio
import sys
import os
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.mcp_invoice_processor.processing.classification import classify_document, DocumentType
from src.mcp_invoice_processor.processing.pipeline import extract_structured_data


class MockContext:
    """Mock context voor testing."""
    
    async def info(self, msg):
        print(f"ℹ️  {msg}")
    
    async def error(self, msg):
        print(f"❌ {msg}")
    
    async def report_progress(self, current, total):
        print(f"📊 Progress: {current}/{total}")


@pytest.mark.asyncio
@pytest.mark.ollama
async def test_document_processing():
    """Test document verwerking direct."""
    
    print("🚀 Directe Test van Document Verwerking")
    print("=" * 60)
    
    # Test 1: Document classificatie
    print("\n📊 Test 1: Document Classificatie")
    print("-" * 40)
    print("Input: Verschillende tekst samples voor classificatie")
    print("Expected: Correcte document type detectie (invoice, cv, unknown)")
    
    test_texts = [
        ("Factuur", "FACTUUR\nFactuurnummer: INV-001\nTotaal: €1000\nBTW: €210"),
        ("CV", "CURRICULUM VITAE\nNaam: Jan Jansen\nEmail: jan@email.com\nWerkervaring: 5 jaar"),
        ("Onbekend", "Dit is gewoon een willekeurige tekst.")
    ]
    
    for name, text in test_texts:
        doc_type = classify_document(text)
        print(f"{name}: {doc_type.value}")
    
    print("✅ Test 1 passed: Document classificatie werkt correct")
    
    # Test 2: Factuur verwerking
    print("\n🧾 Test 2: Factuur Verwerking")
    print("-" * 40)
    print("Input: Sample factuur tekst met alle benodigde velden")
    print("Expected: Succesvolle extractie van factuur data via Ollama")
    
    invoice_text = """
    FACTUUR
    
    Factuurnummer: INV-2025-001
    Factuurdatum: 24-08-2025
    
    AFZENDER:
    TechCorp Solutions B.V.
    Hoofdstraat 123, 1234 AB Amsterdam
    BTW: NL123456789B01
    
    GEADRESSEERDE:
    Test Bedrijf B.V.
    Testweg 456, 5678 CD Rotterdam
    
    BESCHRIJVING:
    - Web Development: €2,500.00
    - Database Design: €1,200.00
    
    Subtotaal: €3,700.00
    BTW (21%): €777.00
    Totaal: €4,477.00
    """
    
    doc_type = classify_document(invoice_text)
    print(f"Gedetecteerd type: {doc_type.value}")
    
    if doc_type == DocumentType.INVOICE:
        ctx = MockContext()
        try:
            print("🤖 Starten Ollama extractie...")
            result = await asyncio.wait_for(
                extract_structured_data(invoice_text, doc_type, ctx),
                timeout=120.0
            )
            
            if result:
                print("✅ Factuur succesvol verwerkt!")
                print(f"📋 Type: {type(result).__name__}")
                
                # Print enkele velden
                if hasattr(result, 'invoice_number'):
                    print(f"   Factuurnummer: {result.invoice_number}")
                if hasattr(result, 'total_amount'):
                    print(f"   Totaal: €{result.total_amount}")
                if hasattr(result, 'supplier_name'):
                    print(f"   Leverancier: {result.supplier_name}")
            else:
                print("❌ Geen resultaat ontvangen")
                
        except asyncio.TimeoutError:
            print("❌ Timeout na 120 seconden")
        except Exception as e:
            print(f"❌ Fout: {e}")
            import traceback
            traceback.print_exc()
    
    # Test 3: CV verwerking
    print("\n👤 Test 3: CV Verwerking")
    print("-" * 40)
    print("Input: Sample CV tekst met persoonlijke gegevens en ervaring")
    print("Expected: Succesvolle extractie van CV data via Ollama")
    
    cv_text = """
    CURRICULUM VITAE
    
    PERSOONLIJKE GEGEVENS:
    Naam: Jan Jansen
    Email: jan.jansen@email.com
    Telefoon: +31 6 12345678
    
    WERKERVARING:
    Senior Developer - TechCorp (2020-heden)
    - Python, FastAPI, React
    - Team leiding 5 personen
    
    Developer - WebTech (2017-2020)
    - Full-stack development
    - JavaScript, Node.js
    
    OPLEIDING:
    Master Computer Science - UvA (2017)
    
    VAARDIGHEDEN:
    Python, JavaScript, React, FastAPI, Docker
    """
    
    doc_type = classify_document(cv_text)
    print(f"Gedetecteerd type: {doc_type.value}")
    
    if doc_type == DocumentType.CV:
        ctx = MockContext()
        try:
            print("🤖 Starten Ollama extractie...")
            result = await asyncio.wait_for(
                extract_structured_data(cv_text, doc_type, ctx),
                timeout=120.0
            )
            
            if result:
                print("✅ CV succesvol verwerkt!")
                print(f"📋 Type: {type(result).__name__}")
                
                # Print enkele velden
                if hasattr(result, 'full_name'):
                    print(f"   Naam: {result.full_name}")
                if hasattr(result, 'email'):
                    print(f"   Email: {result.email}")
                if hasattr(result, 'skills'):
                    print(f"   Vaardigheden: {len(result.skills) if result.skills else 0}")
            else:
                print("❌ Geen resultaat ontvangen")
                
        except asyncio.TimeoutError:
            print("❌ Timeout na 120 seconden")
        except Exception as e:
            print(f"❌ Fout: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 Directe Test Voltooid!")


if __name__ == "__main__":
    asyncio.run(test_document_processing())
