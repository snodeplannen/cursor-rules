import asyncio
import sys
import os
from mcp_invoice_processor.processing.classification import classify_document, DocumentType
from mcp_invoice_processor.processing.pipeline import extract_structured_data
from typing import Any, Dict, List, Optional, Union

"""
Directe test van de pipeline zonder MCP context.
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


async def test_document_processing() -> None:
    """Test document verwerking."""
    print("=== Document Verwerking Test ===")
    
    # Test document inlezen
    with open('test_factuur.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"Document tekst lengte: {len(text)} karakters")
    
    # Document classificatie
    print("\n1. Document Classificatie:")
    doc_type = classify_document(text)
    print(f"   Gedetecteerd type: {doc_type}")
    
    # Mock context maken
    ctx = MockContext()
    
    # Document verwerking
    print("\n2. Document Verwerking:")
    try:
        result = await extract_structured_data(text, doc_type, ctx)
        print(f"   Resultaat: {result}")
        
        if result:
            print(f"   Type: {type(result).__name__}")
            if hasattr(result, 'invoice_number'):
                print(f"   Factuurnummer: {result.invoice_number}")
            if hasattr(result, 'supplier_name'):
                print(f"   Leverancier: {result.supplier_name}")
            if hasattr(result, 'total_amount'):
                print(f"   Totaalbedrag: {result.total_amount}")
        
    except Exception as e:
        print(f"   Fout bij verwerking: {e}")
        import traceback
        traceback.print_exc()
    
    # Context calls tonen
    print(f"\n3. Context Calls:")
    print(f"   Info calls: {len(ctx.info_calls)}")
    print(f"   Error calls: {len(ctx.error_calls)}")
    print(f"   Warning calls: {len(ctx.warning_calls)}")


if __name__ == "__main__":
    asyncio.run(test_document_processing())
