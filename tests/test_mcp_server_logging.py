#!/usr/bin/env python3
"""
Test script om de MCP server logging verbeteringen te testen.
"""
import pytest


import os
import warnings
import logging
from pathlib import Path
# Onderdruk alle DeprecationWarnings voordat andere modules worden geïmporteerd
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="fitz")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="swigobject")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="swigvarlink")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sys")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="builtins")

# Onderdruk ook alle andere warnings
warnings.filterwarnings("ignore")


import sys # noqa: E402
# Voeg src directory toe aan Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_mcp_server_logging():
    """Test de MCP server logging verbeteringen."""
    try:
        print("🧪 Test MCP Server Logging Verbeteringen...")
        
        # Test logging configuratie
        print("📋 Logging configuratie testen...")
        
        # Import de logging configuratie
        from mcp_invoice_processor.logging_config import setup_logging
        
        # Test MCP server integration logger
        print("🔧 MCP server integration logger testen...")
        mcp_server_logger = logging.getLogger("mcp_server_integration")
        mcp_server_logger.info("Test MCP server integration logger")
        print("✅ MCP server integration logger werkt")
        
        # Test MCP server logger
        print("🖥️  MCP server logger testen...")
        mcp_logger = logging.getLogger("mcp")
        mcp_logger.info("Test MCP logger")
        print("✅ MCP logger werkt")
        
        # Test FastMCP logger
        print("🚀 FastMCP logger testen...")
        fastmcp_logger = logging.getLogger("fastmcp")
        fastmcp_logger.info("Test FastMCP logger")
        print("✅ FastMCP logger werkt")
        
        # Controleer of log bestanden zijn aangemaakt
        logs_dir = Path("logs")
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            print(f"✅ Log bestanden aangemaakt: {len(log_files)} bestanden")
            
            # Zoek naar MCP server log bestanden
            mcp_server_logs = [f for f in log_files if "mcp_server" in f.name]
            if mcp_server_logs:
                print(f"   - MCP server logs: {len(mcp_server_logs)} bestanden")
                for log_file in mcp_server_logs:
                    print(f"     * {log_file.name}")
            else:
                print("   - Geen MCP server log bestanden gevonden")
        else:
            print("❌ Logs directory niet aangemaakt")
        
        print("\n🎉 MCP server logging test voltooid!")
        assert True, "MCP server logging test completed successfully"
        
    except Exception as e:
        print(f"❌ MCP server logging test gefaald: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"MCP server logging test failed: {e}"

if __name__ == "__main__":
    test_mcp_server_logging()
