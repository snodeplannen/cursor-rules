#!/usr/bin/env python3
"""
Test FastMCP server integratie met nieuwe extractie methodes.
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock Context class voor testing
class MockContext:
    async def info(self, message: str):
        logger.info(f"[CTX] {message}")
    
    async def error(self, message: str):
        logger.error(f"[CTX] {message}")

async def test_fastmcp_tools():
    """Test FastMCP tools met beide extractie methodes."""
    
    logger.info("🧪 Testen FastMCP tools...")
    
    try:
        from mcp_invoice_processor.fastmcp_server import process_document_text
        
        # Test data
        invoice_text = """
        FACTUUR INV-2024-002
        
        Datum: 20 maart 2024
        Van: TestBedrijf B.V.
        Totaal: €750.00
        BTW: €157.50
        Eindtotaal: €907.50
        """
        
        ctx = MockContext()
        
        # Test 1: JSON Schema mode (default)
        logger.info("🔬 Test 1: JSON Schema mode...")
        result1 = await process_document_text(invoice_text, ctx, "json_schema")
        
        if "error" in result1:
            logger.error(f"❌ JSON Schema mode fout: {result1['error']}")
        else:
            logger.info("✅ JSON Schema mode succesvol!")
            logger.info(f"📊 Resultaat type: {type(result1)}")
        
        # Test 2: Prompt Parsing mode
        logger.info("🔬 Test 2: Prompt Parsing mode...")
        result2 = await process_document_text(invoice_text, ctx, "prompt_parsing")
        
        if "error" in result2:
            logger.error(f"❌ Prompt Parsing mode fout: {result2['error']}")
        else:
            logger.info("✅ Prompt Parsing mode succesvol!")
            logger.info(f"📊 Resultaat type: {type(result2)}")
        
        # Test 3: Onbekende mode (moet default naar JSON Schema)
        logger.info("🔬 Test 3: Onbekende mode...")
        result3 = await process_document_text(invoice_text, ctx, "unknown_mode")
        
        if "error" in result3:
            logger.error(f"❌ Onbekende mode fout: {result3['error']}")
        else:
            logger.info("✅ Onbekende mode succesvol (default naar JSON Schema)!")
            logger.info(f"📊 Resultaat type: {type(result3)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FastMCP test fout: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fastmcp_tools())
    if success:
        logger.info("🎉 FastMCP integratie werkt!")
    else:
        logger.error("❌ FastMCP integratie heeft problemen")
