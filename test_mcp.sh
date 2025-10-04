#!/bin/bash

# Test script voor de MCP Document Processor
# Dit script test de verbinding en functionaliteit van de MCP server

echo "🚀 MCP Document Processor Test Script"
echo "=================================================="

# Controleer of uv beschikbaar is
if ! command -v uv &> /dev/null; then
    echo "❌ uv is niet geïnstalleerd. Installeer eerst uv."
    exit 1
fi

# Controleer of alle bestanden bestaan
if [ ! -f "src/mcp_invoice_processor/fastmcp_server.py" ]; then
    echo "❌ Kan fastmcp_server.py niet vinden. Controleer de projectstructuur."
    exit 1
fi

echo "✅ Projectstructuur gecontroleerd"

# Test de server start
echo "🔌 Testen van server start..."

# Test de nieuwe script commands
echo "🧪 Testen van script commands..."
if timeout 5s uv run mcp-server --help >/dev/null 2>&1; then
    echo "✅ mcp-server script werkt"
else
    echo "⚠️ mcp-server script niet beschikbaar (normaal voor STDIO server)"
fi

# Test HTTP server script
if timeout 5s uv run mcp-http-server-async --help >/dev/null 2>&1; then
    echo "✅ mcp-http-server-async script werkt"
else
    echo "⚠️ mcp-http-server-async script niet beschikbaar"
fi

# Test de server module import
if uv run python -c "import src.mcp_invoice_processor.fastmcp_server; print('✅ MCP server module succesvol geïmporteerd')" >/dev/null 2>&1; then
    echo "✅ MCP server module werkt correct"
else
    echo "❌ MCP server module import mislukt"
    exit 1
fi

# Test de FastMCP CLI
echo "🛠️  Testen van FastMCP CLI..."
if timeout 5s uv run fastmcp --help &>/dev/null; then
    echo "✅ FastMCP CLI werkt"
else
    echo "❌ FastMCP CLI werkt niet"
fi

# Test de dependencies
echo "📦 Testen van dependencies..."
if uv run python -c "import fastmcp, ollama, pydantic; print('✅ Alle dependencies geïmporteerd')" 2>/dev/null; then
    echo "✅ Dependencies werken correct"
else
    echo "❌ Probleem met dependencies"
fi

echo ""
echo "🎯 Alle tests voltooid!"
echo ""
echo "📋 Volgende stappen:"
echo "1. Start Ollama op je systeem"
echo "2. Gebruik mcp_config_cursor.json voor Cursor integratie"
echo "3. Start HTTP server met: uv run python src/mcp_invoice_processor/http_server.py"
echo "4. Test met echte documenten via MCP tools"
echo ""
echo "📚 Zie MCP_USAGE.md voor gedetailleerde instructies"
