#!/usr/bin/env python3
"""
Test script om de verbeterde logging configuratie te testen.
"""

import sys
import os
import asyncio
from pathlib import Path

# Voeg src directory toe aan Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_improved_logging():
    """Test de verbeterde logging configuratie."""
    try:
        print("🧪 Test Verbeterde Logging Configuratie...")
        
        # Import de logging configuratie
        from mcp_invoice_processor.logging_config import setup_logging
        
        # Setup logging
        logger = setup_logging(log_level="DEBUG")
        print("✅ Logging configuratie opgezet")
        
        # Test verschillende log levels
        logger.debug("Dit is een DEBUG bericht")
        logger.info("Dit is een INFO bericht")
        logger.warning("Dit is een WARNING bericht")
        logger.error("Dit is een ERROR bericht")
        
        print("✅ Verschillende log levels getest")
        
        # Test MCP specifieke loggers
        mcp_logger = logger.getChild("mcp")
        mcp_logger.info("MCP logger test bericht")
        
        mcp_server_logger = logger.getChild("mcp.server")
        mcp_server_logger.info("MCP server logger test bericht")
        
        print("✅ MCP loggers getest")
        
        # Controleer of log bestanden zijn aangemaakt
        logs_dir = Path("logs")
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            print(f"✅ Log bestanden aangemaakt: {len(log_files)} bestanden")
            for log_file in log_files:
                print(f"   - {log_file.name}")
        else:
            print("❌ Logs directory niet aangemaakt")
        
        print("\n🎉 Logging test voltooid!")
        return True
        
    except Exception as e:
        print(f"❌ Logging test gefaald: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main functie om async test uit te voeren."""
    try:
        # Maak nieuwe event loop voor de test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Voer async test uit
        success = loop.run_until_complete(test_improved_logging())
        
        # Sluit loop
        loop.close()
        
        return success
        
    except Exception as e:
        print(f"❌ Main functie gefaald: {e}")
        return False

if __name__ == "__main__":
    main()
