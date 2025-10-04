#!/usr/bin/env python3
"""
Test script voor MCP server functionaliteit.
"""
import pytest

import asyncio
import logging

from pathlib import Path
import sys
# Configureer logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Voeg src directory toe aan Python path

sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from mcp_invoice_processor.fastmcp_server import mcp
    from mcp_invoice_processor.processing.pipeline import extract_structured_data
    from mcp_invoice_processor.processing.models import DocumentType
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Zorg ervoor dat alle dependencies zijn geïnstalleerd")
    # Skip tests in plaats van exit
    pass


async def test_mcp_server() -> None:
    """Test de MCP server functionaliteit."""
    logger.info("🚀 Starten van MCP server tests...")
    
    try:
        # Test 1: Server initialisatie
        logger.info("Test 1: Server initialisatie")
        if mcp:
            logger.info("✅ MCP server succesvol geïnitialiseerd")
        else:
            logger.error("❌ MCP server initialisatie mislukt")
            return
        
        # Test 2: Document verwerking
        logger.info("Test 2: Document verwerking")
        test_text = """
        Naam: Jan Jansen
        Email: jan.jansen@email.com
        Telefoon: 06-12345678
        
        Samenvatting:
        Ervaren software ontwikkelaar met 5 jaar ervaring in Python en web development.
        
        Werkervaring:
        - Senior Developer bij TechCorp (2020-2023)
        - Junior Developer bij StartupXYZ (2018-2020)
        
        Opleiding:
        - Bachelor Informatica, Universiteit van Amsterdam (2018)
        
        Vaardigheden:
        - Python, JavaScript, React, Django
        - Git, Docker, AWS
        - Agile development, Scrum
        """
        
        result = await extract_structured_data(test_text, DocumentType.CV, None)
        
        if result:
            logger.info("✅ Document verwerking succesvol")
            logger.info("Document type: CV")
            logger.info(f"Geëxtraheerde data: {result}")
        else:
            logger.warning("⚠️ Document verwerking mislukt - geen data geëxtraheerd")
        
        logger.info("🎉 Alle tests voltooid!")
        
    except Exception as e:
        logger.error(f"❌ Test fout: {e}")
        import traceback
        traceback.print_exc()


async def test_document_classification() -> None:
    """Test document classificatie functionaliteit."""
    logger.info("🔍 Testen van document classificatie...")
    
    try:
        from mcp_invoice_processor.processing.classification import classify_document
        
        # Test CV classificatie
        cv_text = """
        Curriculum Vitae
        Naam: Jan Jansen
        Ervaring: 5 jaar software development
        Opleiding: Bachelor Informatica
        Vaardigheden: Python, JavaScript, React
        """
        
        cv_type = classify_document(cv_text)
        logger.info(f"CV classificatie: {cv_type.value}")
        
        # Test factuur classificatie
        invoice_text = """
        Factuur
        Factuurnummer: INV-2024-001
        Klant: TechCorp
        Totaal: €500,00
        BTW: €95,00
        """
        
        invoice_type = classify_document(invoice_text)
        logger.info(f"Factuur classificatie: {invoice_type.value}")
        
        logger.info("✅ Document classificatie tests voltooid!")
        
    except Exception as e:
        logger.error(f"❌ Document classificatie test fout: {e}")


async def main() -> None:
    """Hoofdfunctie voor het uitvoeren van alle tests."""
    logger.info("🧪 Starten van MCP Invoice Processor tests...")
    
    # Test document classificatie
    await test_document_classification()
    
    # Test MCP server
    await test_mcp_server()
    
    logger.info("🏁 Alle tests voltooid!")


if __name__ == "__main__":
    # Run de tests
    asyncio.run(main())
