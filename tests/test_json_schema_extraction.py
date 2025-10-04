#!/usr/bin/env python3
"""
Test script voor JSON schema extractie vs prompt parsing mode.
"""
import pytest

import asyncio
import logging
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mcp_invoice_processor.processing import ExtractionMethod, extract_structured_data
from mcp_invoice_processor.processing.classification import classify_document

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test invoice data
SAMPLE_INVOICE_TEXT = """
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
Referentie: PROJECT-2024-A
"""

async def test_extraction_methods():
    """Test beide extractie methodes en vergelijk resultaten."""
    
    logger.info("🧪 Starten test van extractie methodes...")
    
    # Classificeer document
    doc_type = classify_document(SAMPLE_INVOICE_TEXT)
    logger.info(f"📋 Document type: {doc_type.value}")
    
    # Test JSON Schema mode (default)
    logger.info("\n🔬 Test 1: JSON Schema Mode")
    try:
        result_schema = await extract_structured_data(
            SAMPLE_INVOICE_TEXT, 
            doc_type, 
            None, 
            ExtractionMethod.JSON_SCHEMA
        )
        logger.info("✅ JSON Schema extractie succesvol")
        if result_schema:
            logger.info(f"📊 Resultaat: {result_schema.invoice_number}, totaal: €{result_schema.total_amount}")
    except Exception as e:
        logger.error(f"❌ JSON Schema extractie gefaald: {e}")
        result_schema = None
    
    # Test Prompt Parsing mode (legacy)
    logger.info("\n🔬 Test 2: Prompt Parsing Mode")
    try:
        result_parsing = await extract_structured_data(
            SAMPLE_INVOICE_TEXT, 
            doc_type, 
            None, 
            ExtractionMethod.PROMPT_PARSING
        )
        logger.info("✅ Prompt Parsing extractie succesvol")
        if result_parsing:
            logger.info(f"📊 Resultaat: {result_parsing.invoice_number}, totaal: €{result_parsing.total_amount}")
    except Exception as e:
        logger.error(f"❌ Prompt Parsing extractie gefaald: {e}")
        result_parsing = None
    
    # Vergelijk resultaten
    logger.info("\n📊 Vergelijking van resultaten:")
    if result_schema and result_parsing:
        logger.info("✅ Beide methodes succesvol")
        logger.info(f"Schema mode - Invoice: {result_schema.invoice_number}, Totaal: €{result_schema.total_amount}")
        logger.info(f"Parsing mode - Invoice: {result_parsing.invoice_number}, Totaal: €{result_parsing.total_amount}")
        
        # Check of resultaten identiek zijn
        if result_schema.model_dump() == result_parsing.model_dump():
            logger.info("🎯 Resultaten zijn identiek!")
        else:
            logger.info("⚠️ Resultaten verschillen")
            
    elif result_schema:
        logger.info("✅ Alleen JSON Schema mode succesvol")
    elif result_parsing:
        logger.info("✅ Alleen Prompt Parsing mode succesvol")
    else:
        logger.info("❌ Beide methodes gefaald")

if __name__ == "__main__":
    asyncio.run(test_extraction_methods())
