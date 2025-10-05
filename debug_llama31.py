#!/usr/bin/env python3
"""
Debug test specifiek voor llama3.1:8b prompt_parsing problemen.
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


async def debug_llama31_prompt_parsing():
    """Debug llama3.1:8b prompt_parsing specifiek."""
    
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
    
    print("🔍 Debug llama3.1:8b prompt_parsing specifiek...")
    
    processor = InvoiceProcessor()
    
    try:
        # Test prompt_parsing methode met llama3.1:8b
        print("\n📝 Test prompt_parsing met llama3.1:8b:")
        result = await processor._extract_with_method(test_text, "prompt_parsing", model="llama3.1:8b")
        
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
    asyncio.run(debug_llama31_prompt_parsing())
