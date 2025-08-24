#!/bin/bash

# Test script voor de MCP Invoice Processor
# Dit script test de verbinding en functionaliteit van de MCP server

echo "🚀 MCP Invoice Processor Test Script"
echo "=================================================="

# Controleer of uv beschikbaar is
if ! command -v uv &> /dev/null; then
    echo "❌ uv is niet geïnstalleerd. Installeer eerst uv."
    exit 1
fi

# Controleer of alle bestanden bestaan
if [ ! -f "src/mcp_invoice_processor/main.py" ]; then
    echo "❌ Kan main.py niet vinden. Controleer de projectstructuur."
    exit 1
fi

echo "✅ Projectstructuur gecontroleerd"

# Test de server start
echo "🔌 Testen van server start..."
timeout 10s uv run python -m src.mcp_invoice_processor.main &
SERVER_PID=$!

# Wacht even tot de server opstart
sleep 3

# Controleer of de server nog draait
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ Server start succesvol"
    
    # Stop de server
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
else
    echo "❌ Server start mislukt"
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
echo "2. Kopieer .env.example naar .env en pas aan"
echo "3. Gebruik de MCP configuratie bestanden"
echo "4. Test met echte PDF documenten"
echo ""
echo "📚 Zie MCP_USAGE.md voor gedetailleerde instructies"
