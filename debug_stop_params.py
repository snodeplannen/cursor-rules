#!/usr/bin/env python3
"""
Debug test met verschillende stop parameters voor llama3.1:8b.
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


async def debug_stop_parameters():
    """Debug verschillende stop parameters voor llama3.1:8b."""
    
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
    
    print("🔍 Debug stop parameters voor llama3.1:8b...")
    
    processor = InvoiceProcessor()
    prompt = processor.get_extraction_prompt(test_text, "prompt_parsing")
    
    # Test verschillende stop parameter configuraties
    stop_configs = [
        {"name": "Geen stop parameters", "stop": None},
        {"name": "Alleen ```", "stop": ["```"]},
        {"name": "Originele config", "stop": ["```", "```json", "```\n", "\n\n\n"]},
        {"name": "Minder agressief", "stop": ["```json", "```\n"]},
    ]
    
    for config in stop_configs:
        print(f"\n🧪 Test: {config['name']}")
        print("-" * 40)
        
        try:
            options = {
                "temperature": 0.1,
                "num_predict": 2048,
            }
            if config['stop']:
                options["stop"] = config['stop']
            
            response = ollama.chat(
                model="llama3.1:8b",
                messages=[{"role": "user", "content": prompt}],
                options=options
            )
            
            response_content = response['message']['content'].strip()
            print(f"📄 Response ({len(response_content)} chars):")
            if response_content:
                print(response_content[:200] + "..." if len(response_content) > 200 else response_content)
            else:
                print("(Lege response)")
                
        except Exception as e:
            print(f"❌ Exception: {e}")


if __name__ == "__main__":
    asyncio.run(debug_stop_parameters())
