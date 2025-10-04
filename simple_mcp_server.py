#!/usr/bin/env python3
"""
Eenvoudige MCP Server voor document verwerking met modulaire processors.

DEPRECATED: Gebruik fastmcp_server.py in plaats daarvan voor volledige functionaliteit.
Dit script is alleen voor referentie en demonstratie.
"""

import sys
from pathlib import Path

# Voeg src toe aan Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("⚠️ DEPRECATED: Dit script gebruikt de oude MCP SDK.")
print("✅ Gebruik in plaats daarvan:")
print("   - STDIO: uv run python src/mcp_invoice_processor/fastmcp_server.py")
print("   - HTTP:  uv run python src/mcp_invoice_processor/http_server.py")
print()
print("De nieuwe FastMCP server biedt:")
print("  - Modulaire processor architecture (InvoiceProcessor, CVProcessor)")
print("  - Parallel document classification")
print("  - Realtime progress reporting")
print("  - Comprehensive statistics")
print("  - MCP Resources support")
print("  - HTTP transport voor web integratie")
print()

if __name__ == "__main__":
    print("Start de server met:")
    print("  STDIO: uv run python src/mcp_invoice_processor/fastmcp_server.py")
    print("  HTTP:  uv run python src/mcp_invoice_processor/http_server.py")
