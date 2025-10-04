#!/usr/bin/env python3
"""
Vergelijking van JSON schema vs prompt parsing mode met v2.0 processors.
"""

import asyncio
import logging
import pytest

from mcp_invoice_processor.processors.invoice import InvoiceProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DETAILED_INVOICE_TEXT = """
FACTUUR

Factuurnummer: INV-2024-001
Factuurdatum: 15 maart 2024
Vervaldatum: 15 april 2024

Van:
TechCorp B.V.
Techstraat 123
1234 AB Amsterdam
BTW: NL123456789B01

Aan:
ClientCorp B.V.
Clientlaan 456
5678 CD Rotterdam
BTW: NL987654321B01

Omschrijving                    Aantal  Prijs    Totaal
Softwarelicentie                    1   €500,00  €500,00
Consultancy uren                   10   €75,00   €750,00
Support contract                    1   €200,00  €200,00

Subtotaal:                                      €1.450,00
BTW (21%):                                       €304,50
Totaal:                                        €1.754,50

Betalingsvoorwaarden: 30 dagen
Betalingsmethode: Bankoverschrijving
Referentie: PROJECT-2024-A

Opmerkingen: Bedankt voor uw opdracht!
"""


class MockContext:
    async def info(self, msg, extra=None): logger.info(msg)
    async def debug(self, msg, extra=None): logger.debug(msg)
    async def warning(self, msg, extra=None): logger.warning(msg)
    async def error(self, msg, extra=None): logger.error(msg)
    async def report_progress(self, progress, total=100): pass


@pytest.mark.asyncio
async def test_json_vs_prompt_comparison():
    """Vergelijk JSON schema vs prompt parsing modes."""
    print("\n=== JSON SCHEMA VS PROMPT PARSING (v2.0) ===\n")
    
    processor = InvoiceProcessor()
    ctx = MockContext()
    
    # JSON Schema mode
    logger.info("🔧 JSON Schema Mode...")
    result_json = await processor.extract(DETAILED_INVOICE_TEXT, ctx, "json_schema")
    
    # Prompt Parsing mode  
    logger.info("🔧 Prompt Parsing Mode...")
    result_prompt = await processor.extract(DETAILED_INVOICE_TEXT, ctx, "prompt_parsing")
    
    if result_json and result_prompt:
        # Validatie
        _, json_complete, _ = await processor.validate_extracted_data(result_json, ctx)
        _, prompt_complete, _ = await processor.validate_extracted_data(result_prompt, ctx)
        
        print(f"\n📊 RESULTATEN:")
        print(f"  JSON Schema   - {json_complete:.1f}% compleet")
        print(f"  Prompt Parsing - {prompt_complete:.1f}% compleet")
        
        if json_complete > prompt_complete:
            print(f"  🏆 WINNAAR: JSON Schema")
        elif prompt_complete > json_complete:
            print(f"  🏆 WINNAAR: Prompt Parsing")
        else:
            print(f"  🤝 GELIJK")
    
    print()


if __name__ == "__main__":
    asyncio.run(test_json_vs_prompt_comparison())
