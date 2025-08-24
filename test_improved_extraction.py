#!/usr/bin/env python3
"""
Test script voor verbeterde extractie met betere document classificatie.
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_invoice_processor.processing import ExtractionMethod, extract_structured_data
from mcp_invoice_processor.processing.classification import classify_document

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Duidelijke invoice tekst
CLEAR_INVOICE_TEXT = """
FACTUUR INV-2024-001

Factuurdatum: 15 maart 2024
Vervaldatum: 15 april 2024

Van: TechCorp B.V.
Aan: ClientCorp B.V.

Omschrijving: Softwarelicentie
Aantal: 1
Prijs: €500,00
Totaal: €500,00

BTW: €105,00
Eindtotaal: €605,00
"""

async def test_improved_system():
    """Test het verbeterde systeem."""
    
    logger.info("🧪 Testen verbeterd extractie systeem...")
    
    # Test classificatie
    doc_type = classify_document(CLEAR_INVOICE_TEXT)
    logger.info(f"📋 Document type: {doc_type.value}")
    
    if doc_type.value == "unknown":
        logger.error("❌ Document nog steeds geclassificeerd als unknown!")
        return False
    
    # Test JSON Schema extractie
    logger.info("🔬 Testen JSON Schema extractie...")
    try:
        result = await extract_structured_data(
            CLEAR_INVOICE_TEXT, 
            doc_type, 
            None, 
            ExtractionMethod.JSON_SCHEMA
        )
        
        if result:
            logger.info("✅ JSON Schema extractie succesvol!")
            logger.info(f"📊 Invoice: {result.invoice_number}")
            logger.info(f"💰 Totaal: €{result.total_amount}")
            logger.info(f"🏢 Leverancier: {result.supplier_name}")
            return True
        else:
            logger.error("❌ JSON Schema extractie gaf None terug")
            return False
            
    except Exception as e:
        logger.error(f"❌ JSON Schema extractie fout: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_improved_system())
    if success:
        logger.info("🎉 Verbeterd systeem werkt!")
    else:
        logger.error("❌ Systeem heeft nog problemen")
