#!/usr/bin/env python3
"""
Debug test voor prompt_parsing problemen.
"""

import asyncio
import sys
from pathlib import Path

# Voeg src toe aan Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_invoice_processor.tools import process_document_text


async def debug_prompt_parsing():
    """Debug prompt_parsing problemen."""
    
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
    
    print("🔍 Debug prompt_parsing problemen...")
    
    try:
        # Test prompt_parsing methode
        print("\n📝 Test prompt_parsing methode:")
        result = await process_document_text(test_text, "prompt_parsing")
        
        print(f"   Resultaat: {result}")
        
        if "error" in result:
            print(f"   ❌ Fout: {result['error']}")
        else:
            print(f"   ✅ Succes: {result.get('document_type', 'unknown')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_prompt_parsing())
