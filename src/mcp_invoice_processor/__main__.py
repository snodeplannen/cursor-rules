#!/usr/bin/env python3
"""
Main entry point voor de MCP Invoice Processor.
Onderdrukt warnings voordat de server start.
"""

import warnings
import sys
import os

# Voeg src directory toe aan Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Onderdruk alle DeprecationWarnings voordat andere modules worden geïmporteerd
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="fitz")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="swigobject")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="swigvarlink")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sys")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="builtins")

def main():
    """Start de MCP server."""
    try:
        # Import en start de server
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Start de server
        mcp.run()
        
    except Exception as e:
        print(f"Fout bij starten MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
