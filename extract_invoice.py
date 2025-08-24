#!/usr/bin/env python3
"""
Script om de Amazon rugtas factuur te verwerken en gestructureerde data te extraheren.
"""

import asyncio
import fitz  # type: ignore
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_invoice_processor.processing.pipeline import extract_structured_data
from mcp_invoice_processor.processing.classification import classify_document
from mcp_invoice_processor.processing.models import DocumentType

async def main():
    """Hoofdfunctie voor factuur verwerking."""
    print("=== AMAZON RUGTAS FACTUUR VERWERKING ===")
    
    try:
        # 1. PDF tekst extraheren
        print("📄 PDF tekst extraheren...")
        doc = fitz.open('amazon_rugtas-factuur.pdf')
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        print(f"✅ Tekst geëxtraheerd: {len(text)} karakters")
        
        # 2. Document type classificeren
        print("📊 Document type classificeren...")
        doc_type = classify_document(text)
        print(f"✅ Document type: {doc_type.value}")
        
        # 3. AI-gebaseerde data extractie
        print("🤖 Starten AI-gebaseerde data extractie...")
        result = await extract_structured_data(text, DocumentType.INVOICE)
        
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
            
            print("\n=== SAMENVATTING ===")
            print(f"✅ Factuur succesvol verwerkt!")
            print(f"📊 Totaal bedrag: €{result.total_amount}")
            print(f"🏢 Klant: {result.customer_name}")
            print(f"📦 Producten: {len(result.line_items)} regels")
            
        else:
            print("❌ Data extractie mislukt")
            
    except Exception as e:
        print(f"❌ Fout bij verwerken factuur: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== EINDE VERWERKING ===")

if __name__ == "__main__":
    asyncio.run(main())



