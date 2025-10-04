import asyncio
import sys
import os
from mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf
from mcp_invoice_processor.processing.classification import classify_document, DocumentType
from mcp_invoice_processor.processing.pipeline import extract_structured_data
from typing import Any, Dict, List, Optional, Union
import pytest

"""
Directe test van Amazon rugtas factuur PDF verwerking.
"""

# Voeg src directory toe aan Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))



class MockContext:
    """Mock context voor testing."""
    
    def __init__(self) -> None:
        self.info_calls = []
        self.error_calls = []
        self.warning_calls = []
    
    async def info(self, message: str) -> None:
        """Mock info methode."""
        self.info_calls.append(message)
        print(f"INFO: {message}")
    
    async def error(self, message: str) -> None:
        """Mock error methode."""
        self.error_calls.append(message)
        print(f"ERROR: {message}")
    
    async def warning(self, message: str) -> None:
        """Mock warning methode."""
        self.warning_calls.append(message)
        print(f"WARNING: {message}")


async def test_amazon_invoice() -> None:
    """Test Amazon rugtas factuur verwerking."""
    print("=== Amazon Rugtas Factuur Verwerking Test ===")
    
    pdf_file = "amazon_rugtas-factuur.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF bestand niet gevonden: {pdf_file}")
        return
    
    try:
        # Stap 1: PDF inlezen
        print(f"\n1. PDF Bestand Inlezen: {pdf_file}")
        with open(pdf_file, 'rb') as f:
            pdf_bytes = f.read()
        print(f"   PDF grootte: {len(pdf_bytes)} bytes")
        
        # Stap 2: Tekst extraheren
        print("\n2. Tekst Extractie uit PDF:")
        text = extract_text_from_pdf(pdf_bytes)
        print(f"   Geëxtraheerde tekst lengte: {len(text)} karakters")
        print(f"   Eerste 200 karakters: {text[:200]}...")
        
        # Stap 3: Document classificatie
        print("\n3. Document Classificatie:")
        doc_type = classify_document(text)
        print(f"   Gedetecteerd type: {doc_type}")
        
        # Stap 4: Gestructureerde data extractie
        print("\n4. Gestructureerde Data Extractie:")
        ctx = MockContext()
        
        result = await extract_structured_data(text, doc_type, ctx)
        
        if result:
            print("   ✅ Extractie succesvol!")
            print(f"   Type: {type(result).__name__}")
            
            # Toon factuur details
            if hasattr(result, 'invoice_number'):
                print(f"   Factuurnummer: {result.invoice_number}")
            if hasattr(result, 'supplier_name'):
                print(f"   Leverancier: {result.supplier_name}")
            if hasattr(result, 'total_amount'):
                print(f"   Totaalbedrag: {result.total_amount}")
            if hasattr(result, 'line_items'):
                print(f"   Aantal producten: {len(result.line_items)}")
                for i, item in enumerate(result.line_items):
                    print(f"     {i+1}. {item.description} - {item.quantity}x €{item.unit_price} = €{item.line_total}")
        else:
            print("   ❌ Extractie mislukt")
        
        # Context calls tonen
        print(f"\n5. Context Calls:")
        print(f"   Info calls: {len(ctx.info_calls)}")
        print(f"   Error calls: {len(ctx.error_calls)}")
        print(f"   Warning calls: {len(ctx.warning_calls)}")
        
    except Exception as e:
        print(f"❌ Fout bij verwerking: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_amazon_invoice())
