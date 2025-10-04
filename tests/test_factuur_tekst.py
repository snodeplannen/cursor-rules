#!/usr/bin/env python3
"""
Script om de factuurtekst "factuurn 6666" te verwerken met nieuwe v2.0 processors.
"""

import asyncio
import pytest
from mcp_invoice_processor.processors import get_registry
from mcp_invoice_processor.processors.invoice import InvoiceProcessor


class MockContext:
    """Mock context voor testing."""
    async def info(self, msg, extra=None): print(f"INFO: {msg}")
    async def debug(self, msg, extra=None): print(f"DEBUG: {msg}")
    async def warning(self, msg, extra=None): print(f"WARN: {msg}")
    async def error(self, msg, extra=None): print(f"ERROR: {msg}")
    async def report_progress(self, progress, total=100): pass


@pytest.mark.asyncio
async def test_factuur_tekst():
    """Test factuur tekst verwerking met v2.0 processors."""
    print("=== FACTUUR TEKST VERWERKING (v2.0) ===")
    
    # Test tekst
    test_text = "factuurn 6666"
    print(f"📄 Verwerken tekst: '{test_text}'")
    
    try:
        # 1. Document type classificeren via registry
        print("\n📊 Document type classificeren (parallel)...")
        registry = get_registry()
        ctx = MockContext()
        
        doc_type, confidence, processor = await registry.classify_document(test_text, ctx)
        print(f"✅ Document type: {doc_type}")
        print(f"✅ Confidence: {confidence:.1f}%")
        print(f"✅ Processor: {processor.tool_name if processor else 'None'}")
        
        # 2. AI-gebaseerde data extractie
        if processor:
            print("\n🤖 Starten AI-gebaseerde data extractie...")
            result = await processor.extract(test_text, ctx, method="hybrid")
            
            if result:
                print("\n=== GEEXTRACHTE FACTUUR DATA ===")
                print(f"Factuurnummer: {result.invoice_number}")
                print(f"Factuur ID: {result.invoice_id}")
                print(f"Factuurdatum: {result.invoice_date}")
                print(f"Klant: {result.customer_name}")
                print(f"Klant adres: {result.customer_address}")
                print(f"Leverancier: {result.supplier_name}")
                print(f"Leverancier adres: {result.supplier_address}")
                print(f"Leverancier BTW: {result.supplier_vat_number}")
                print(f"Subtotaal: €{result.subtotal}")
                print(f"BTW bedrag: €{result.vat_amount}")
                print(f"Totaal bedrag: €{result.total_amount}")
                print(f"Valuta: {result.currency}")
                print(f"Referentie: {result.reference}")
                
                print("\n=== PRODUCT DETAILS ===")
                for i, item in enumerate(result.line_items):
                    print(f"\nProduct {i+1}:")
                    print(f"  Beschrijving: {item.description}")
                    print(f"  Aantal: {item.quantity}")
                    print(f"  Eenheidsprijs: €{item.unit_price}")
                    print(f"  Regeltotaal: €{item.line_total}")
                    print(f"  BTW percentage: {item.vat_rate}%")
                    print(f"  BTW bedrag: €{item.vat_amount}")
                
                # Validatie
                is_valid, completeness, issues = await processor.validate_extracted_data(result, ctx)
                print("\n=== VALIDATIE ===")
                print(f"✅ Valid: {is_valid}")
                print(f"📊 Completeness: {completeness:.1f}%")
                if issues:
                    print(f"⚠️ Issues: {', '.join(issues)}")
                
                print("\n=== SAMENVATTING ===")
                print(f"✅ Factuur succesvol verwerkt!")
                print(f"📊 Totaal bedrag: €{result.total_amount}")
                print(f"🏢 Klant: {result.customer_name}")
                print(f"📦 Producten: {len(result.line_items)} regels")
                
            else:
                print("❌ Data extractie mislukt")
        else:
            print("❌ Geen geschikte processor gevonden")
            
    except Exception as e:
        print(f"❌ Fout bij verwerken factuur: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    print("\n=== EINDE VERWERKING ===")


if __name__ == "__main__":
    asyncio.run(test_factuur_tekst())

