#!/usr/bin/env python3
"""
Debug test voor JSON schema mode om lege resultaten te analyseren.
"""

import asyncio
import logging
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_invoice_processor.processing import ExtractionMethod, extract_structured_data
from mcp_invoice_processor.processing.classification import classify_document
from mcp_invoice_processor.processing.models import InvoiceData

# Setup debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test invoice data met alle mogelijke velden
COMPREHENSIVE_INVOICE_TEXT = """
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

Subtotaal:                                      €1.250,00
BTW (21%):                                       €262,50
Totaal:                                        €1.512,50

Betalingsvoorwaarden: 30 dagen
Betalingsmethode: Bankoverschrijving
Referentie: PROJECT-2024-A

Opmerkingen: Bedankt voor uw opdracht!
"""

async def debug_json_schema():
    """Debug JSON schema mode stap voor stap."""
    
    logger.info("🔍 Debug JSON Schema Mode...")
    
    # Stap 1: Classificatie
    doc_type = classify_document(COMPREHENSIVE_INVOICE_TEXT)
    logger.info(f"📋 Document type: {doc_type.value}")
    
    # Stap 2: JSON Schema generatie
    schema = InvoiceData.model_json_schema()
    logger.info(f"📊 Schema gegenereerd met {len(schema.get('properties', {}))} properties")
    logger.debug(f"Schema keys: {list(schema.get('properties', {}).keys())}")
    
    # Stap 3: Test beide methodes met debug output
    logger.info("\n🔬 Test JSON Schema Mode...")
    try:
        result_schema = await extract_structured_data(
            COMPREHENSIVE_INVOICE_TEXT, 
            doc_type, 
            None, 
            ExtractionMethod.JSON_SCHEMA
        )
        
        if result_schema:
            logger.info("✅ JSON Schema mode succesvol!")
            logger.info(f"📊 Type: {type(result_schema)}")
            logger.info(f"📋 Invoice ID: {result_schema.invoice_id}")
            logger.info(f"📋 Invoice Number: {result_schema.invoice_number}")
            logger.info(f"💰 Total: €{result_schema.total_amount}")
            logger.info(f"🏢 Supplier: {result_schema.supplier_name}")
            logger.info(f"👥 Customer: {result_schema.customer_name}")
            logger.info(f"📦 Line items: {len(result_schema.line_items)}")
            
            # Print alle velden
            logger.info("\n📋 Alle velden:")
            data_dict = result_schema.model_dump()
            for key, value in data_dict.items():
                if isinstance(value, list) and len(value) > 0:
                    logger.info(f"   {key}: {len(value)} items")
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            logger.info(f"     [{i}]: {item}")
                        else:
                            logger.info(f"     [{i}]: {item}")
                else:
                    logger.info(f"   {key}: {value}")
        else:
            logger.error("❌ JSON Schema mode gaf None terug!")
            
    except Exception as e:
        logger.error(f"❌ JSON Schema mode fout: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    logger.info("\n🔬 Test Prompt Parsing Mode...")
    try:
        result_parsing = await extract_structured_data(
            COMPREHENSIVE_INVOICE_TEXT, 
            doc_type, 
            None, 
            ExtractionMethod.PROMPT_PARSING
        )
        
        if result_parsing:
            logger.info("✅ Prompt Parsing mode succesvol!")
            logger.info(f"📊 Type: {type(result_parsing)}")
            logger.info(f"📋 Invoice ID: {result_parsing.invoice_id}")
            logger.info(f"📋 Invoice Number: {result_parsing.invoice_number}")
            logger.info(f"💰 Total: €{result_parsing.total_amount}")
            logger.info(f"🏢 Supplier: {result_parsing.supplier_name}")
            logger.info(f"👥 Customer: {result_parsing.customer_name}")
            logger.info(f"📦 Line items: {len(result_parsing.line_items)}")
        else:
            logger.error("❌ Prompt Parsing mode gaf None terug!")
            
    except Exception as e:
        logger.error(f"❌ Prompt Parsing mode fout: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(debug_json_schema())
