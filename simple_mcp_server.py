#!/usr/bin/env python3
"""
Eenvoudige MCP Server voor document verwerking met v2.0 processors.

DEPRECATED: Gebruik fastmcp_server.py in plaats daarvan voor volledige functionaliteit.
Dit script is alleen voor referentie.
"""

import sys
from pathlib import Path

# Voeg src toe aan Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("⚠️ DEPRECATED: Dit script gebruikt de oude MCP SDK.")
print("✅ Gebruik in plaats daarvan: uv run python -m mcp_invoice_processor")
print("   Of: uv run python -m mcp_invoice_processor.fastmcp_server")
print()
print("De nieuwe FastMCP server biedt:")
print("  - Modulaire processor architecture")
print("  - Parallel document classification")
print("  - Realtime progress reporting")
print("  - Comprehensive statistics")
print("  - MCP Resources support")
print()

if __name__ == "__main__":
    print("Start de server met: uv run python -m mcp_invoice_processor")
