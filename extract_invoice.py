#!/usr/bin/env python3
"""
Script om Amazon rugtas factuur te verwerken met v2.0 processors.
"""

import asyncio
import fitz  # PyMuPDF
from pathlib import Path

from mcp_invoice_processor.processors import get_registry
from mcp_invoice_processor.processors.invoice import InvoiceProcessor


async def main() -> None:
    """Hoofdfunctie voor factuur verwerking met v2.0."""
    print("=== AMAZON RUGTAS FACTUUR VERWERKING (v2.0) ===")
    
    try:
        # 1. PDF tekst extraheren
        print("📄 PDF tekst extraheren...")
        doc = fitz.open('amazon_rugtas-factuur.pdf')
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        print(f"✅ Tekst geëxtraheerd: {len(text)} karakters")
        
        # 2. Document type classificeren via registry
        print("📊 Document type classificeren...")
        registry = get_registry()
        doc_type, confidence, processor = await registry.classify_document(text, None)
        print(f"✅ Document type: {doc_type} ({confidence:.1f}% confidence)")
        
        # 3. AI-gebaseerde data extractie
        if processor:
            print("🤖 Starten AI-gebaseerde data extractie...")
            result = await processor.extract(text, None, method="hybrid")
            
            if result:
                from mcp_invoice_processor.processors.invoice.models import InvoiceData
                # Type narrowing voor mypy
                assert isinstance(result, InvoiceData), "Result must be InvoiceData"
                print("\n=== GEEXTRACHTE FACTUUR DATA ===")
                # Type narrowing voor mypy
                if hasattr(result, 'invoice_number'):
                    print(f"Factuurnummer: {result.invoice_number}")
                if hasattr(result, 'invoice_id'):
                    print(f"Factuur ID: {result.invoice_id}")
                if hasattr(result, 'invoice_date'):
                    print(f"Factuurdatum: {result.invoice_date}")
                if hasattr(result, 'customer_name'):
                    print(f"Klant: {result.customer_name}")
                if hasattr(result, 'customer_address'):
                    print(f"Klant adres: {result.customer_address}")
                if hasattr(result, 'supplier_name'):
                    print(f"Leverancier: {result.supplier_name}")
                if hasattr(result, 'supplier_address'):
                    print(f"Leverancier adres: {result.supplier_address}")
                if hasattr(result, 'supplier_vat_number'):
                    print(f"Leverancier BTW: {result.supplier_vat_number}")
                if hasattr(result, 'subtotal'):
                    print(f"Subtotaal: €{result.subtotal}")
                if hasattr(result, 'vat_amount'):
                    print(f"BTW bedrag: €{result.vat_amount}")
                if hasattr(result, 'total_amount'):
                    print(f"Totaal bedrag: €{result.total_amount}")
                if hasattr(result, 'currency'):
                    print(f"Valuta: {result.currency}")
                if hasattr(result, 'reference'):
                    print(f"Referentie: {result.reference}")
                
                if hasattr(result, 'line_items'):
                    print("\n=== PRODUCT DETAILS ===")
                    for i, item in enumerate(result.line_items):
                        print(f"\nProduct {i+1}:")
                        print(f"  Beschrijving: {item.description}")
                        print(f"  Aantal: {item.quantity}")
                        print(f"  Eenheidsprijs: €{item.unit_price}")
                        print(f"  Regeltotaal: €{item.line_total}")
                        if item.vat_rate:
                            print(f"  BTW percentage: {item.vat_rate}%")
                        if item.vat_amount:
                            print(f"  BTW bedrag: €{item.vat_amount}")
                    
                    print("\n=== SAMENVATTING ===")
                    print("✅ Factuur succesvol verwerkt!")
                    print(f"📊 Totaal bedrag: €{result.total_amount}")
                    print(f"🏢 Klant: {result.customer_name}")
                    print(f"📦 Producten: {len(result.line_items) if result.line_items else 0} regels")
            else:
                print("❌ Data extractie mislukt")
        else:
            print("❌ Geen geschikte processor gevonden")
            
    except Exception as e:
        print(f"❌ Fout bij verwerken factuur: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== EINDE VERWERKING ===")


if __name__ == "__main__":
    asyncio.run(main())
