#!/usr/bin/env python3
"""
Test script om specifieke errors in het systeem te analyseren.
"""
import pytest

import asyncio
import logging
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Setup verbose logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_imports():
    """Test alle imports om import errors te vinden."""
    logger.info("🔍 Testen imports...")
    
    try:
        from mcp_invoice_processor.processing import ExtractionMethod, extract_structured_data
        logger.info("✅ Import ExtractionMethod en extract_structured_data succesvol")
    except Exception as e:
        logger.error(f"❌ Import fout: {e}")
        return False
    
    try:
        from mcp_invoice_processor.processing.classification import classify_document
        logger.info("✅ Import classify_document succesvol")
    except Exception as e:
        logger.error(f"❌ Import fout: {e}")
        return False
    
    try:
        from mcp_invoice_processor.processing.models import DocumentType, InvoiceData
        logger.info("✅ Import models succesvol")
    except Exception as e:
        logger.error(f"❌ Import fout: {e}")
        return False
        
    return True

async def test_simple_extraction():
    """Test een zeer eenvoudige extractie."""
    logger.info("🧪 Testen eenvoudige extractie...")
    
    try:
        from mcp_invoice_processor.processing import ExtractionMethod, extract_structured_data
        from mcp_invoice_processor.processing.classification import classify_document
        
        # Zeer eenvoudige test tekst
        simple_text = """
        Factuur INV-001
        Datum: 1 januari 2024
        Totaal: €100.00
        """
        
        # Classificeer
        doc_type = classify_document(simple_text)
        logger.info(f"📋 Document type: {doc_type.value}")
        
        # Test JSON Schema mode
        logger.info("🔬 Testen JSON Schema mode...")
        try:
            result = await extract_structured_data(
                simple_text, 
                doc_type, 
                None, 
                ExtractionMethod.JSON_SCHEMA
            )
            if result:
                logger.info("✅ JSON Schema mode succesvol")
                logger.info(f"📊 Invoice number: {result.invoice_number}")
            else:
                logger.error("❌ JSON Schema mode gaf None terug")
        except Exception as e:
            logger.error(f"❌ JSON Schema mode fout: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test fout: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

async def test_ollama_connection():
    """Test Ollama verbinding."""
    logger.info("🌐 Testen Ollama verbinding...")
    
    try:
        import ollama
        
        # Test eenvoudige chat
        response = ollama.chat(
            model='llama3.1',
            messages=[
                {
                    'role': 'user',
                    'content': 'Zeg gewoon "test" terug.'
                }
            ]
        )
        
        logger.info("✅ Ollama verbinding succesvol")
        logger.info(f"📨 Response: {response['message']['content']}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ollama verbinding fout: {e}")
        return False

async def main():
    """Hoofdtest functie."""
    logger.info("🚀 Starten error analyse...")
    
    # Test 1: Imports
    imports_ok = await test_imports()
    if not imports_ok:
        logger.error("❌ Imports gefaald - stoppen met testen")
        return
    
    # Test 2: Ollama verbinding
    ollama_ok = await test_ollama_connection()
    if not ollama_ok:
        logger.error("❌ Ollama verbinding gefaald - stoppen met testen")
        return
    
    # Test 3: Eenvoudige extractie
    extraction_ok = await test_simple_extraction()
    
    if imports_ok and ollama_ok and extraction_ok:
        logger.info("🎉 Alle tests succesvol!")
    else:
        logger.error("❌ Sommige tests gefaald")

if __name__ == "__main__":
    asyncio.run(main())
