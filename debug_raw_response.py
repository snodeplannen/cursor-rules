#!/usr/bin/env python3
"""
Debug test om de raw LLM response te bekijken voor llama3.1:8b.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Voeg src toe aan Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import ollama
from mcp_invoice_processor.processors.invoice.processor import InvoiceProcessor

# Setup debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def debug_raw_response():
    """Debug raw LLM response voor llama3.1:8b."""
    
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
    
    print("🔍 Debug raw LLM response voor llama3.1:8b...")
    
    processor = InvoiceProcessor()
    
    try:
        # Haal prompt op
        prompt = processor.get_extraction_prompt(test_text, "prompt_parsing")
        print(f"\n📝 Prompt length: {len(prompt)} characters")
        
        # Direct Ollama call
        print("\n🤖 Direct Ollama call met llama3.1:8b:")
        response = ollama.chat(
            model="llama3.1:8b",
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0.1,
                "num_predict": 2048,
                "stop": ["```", "```json", "```\n", "\n\n\n"]
            }
        )
        
        response_content = response['message']['content'].strip()
        print(f"\n📄 Raw response ({len(response_content)} chars):")
        print("=" * 60)
        print(response_content)
        print("=" * 60)
        
        # Test JSON extractie
        print("\n🔍 Test JSON extractie:")
        json_str = processor._extract_json_from_response(response_content, "prompt_parsing")
        
        if json_str:
            print(f"✅ JSON gevonden ({len(json_str)} chars):")
            print(json_str)
        else:
            print("❌ Geen JSON gevonden")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_raw_response())
