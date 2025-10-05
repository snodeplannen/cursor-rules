#!/usr/bin/env python3
"""
Direct debug van InvoiceProcessor prompt_parsing.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Voeg src toe aan Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_invoice_processor.processors.invoice.processor import InvoiceProcessor

# Setup debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def debug_invoice_processor():
    """Debug InvoiceProcessor prompt_parsing direct."""
    
    test_text = """
    Factuur #12345
    Datum: 2024-01-15
    Van: Test Bedrijf BV
    Naar: Klant Bedrijf NV
    Bedrag: €1,234.56
    BTW: €258.26
    Totaal: €1,492.82
    
    Beschrijving: Web development services
    """
    
    print("🔍 Debug InvoiceProcessor prompt_parsing direct...")
    
    processor = InvoiceProcessor()
    
    try:
        # Test prompt_parsing methode direct
        print("\n📝 Test prompt_parsing methode direct:")
        result = await processor._extract_with_method(test_text, "prompt_parsing")
        
        print(f"   Resultaat: {result}")
        
        if result is None:
            print("   ❌ Resultaat is None - extractie mislukt")
        else:
            print(f"   ✅ Succes: {result}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_invoice_processor())
