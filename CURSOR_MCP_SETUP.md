# 🚀 MCP Server Activatie in Cursor

Deze gids helpt je om de MCP Invoice Processor te activeren in Cursor.

## 📋 Vereisten

- ✅ Cursor geïnstalleerd
- ✅ Ollama server draaiend op `localhost:11434`
- ✅ Project dependencies geïnstalleerd met `uv sync --dev`

## 🔧 Stap 1: MCP Configuratie Bestand

Het `mcp.json` bestand is al geconfigureerd en getest. Het bevat:

```json
{
  "mcpServers": {
    "mcp-invoice-processor": {
      "command": "C:\\ProgramData\\miniforge3\\Scripts\\uv.exe",
      "args": [
        "--directory",
        "C:\\py_cursor-rules\\cursor_ratsenbergertest\\",
        "run",
        "python",
        "-m",
        "src.mcp_invoice_processor.fastmcp_server"
      ],
      "env": {
        "LOG_LEVEL": "INFO",
        "OLLAMA_HOST": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3",
        "OLLAMA_TIMEOUT": "120"
      }
    }
  }
}
```

## 📁 Stap 2: Cursor Configuratie Directory

### Windows
Kopieer `mcp.json` naar een van deze locaties:

**Optie 1: User Directory (Aanbevolen)**
```
%APPDATA%\Cursor\User\mcp.json
```

**Optie 2: Workspace Directory**
```
C:\py_cursor-rules\cursor_ratsenbergertest\.cursor\mcp.json
```

### macOS/Linux
```bash
# User directory
cp mcp.json ~/Library/Application\ Support/Cursor/User/mcp.json

# Workspace directory
cp mcp.json .cursor/mcp.json
```

## 🔄 Stap 3: Cursor Herstarten

1. Sluit Cursor volledig af
2. Start Cursor opnieuw op
3. Open het project opnieuw

## ✅ Stap 4: Verificatie

Na het herstarten zou je moeten zien:

1. **Command Palette**: Druk `Ctrl+Shift+P` (Windows) of `Cmd+Shift+P` (macOS)
2. **Zoek naar**: `MCP` of `mcp-invoice-processor`
3. **Verwacht resultaat**: Je zou MCP-gerelateerde commando's moeten zien

## 🧪 Stap 5: Testen

### Test 1: Server Beschikbaarheid
```bash
# In Cursor terminal of command palette
/mcp-invoice-processor health_check
```

### Test 2: Document Classificatie
```bash
# Test document classificatie
/mcp-invoice-processor classify_document_type "Dit is een test CV document"
```

### Test 3: Document Verwerking
```bash
# Test volledige document verwerking
/mcp-invoice-processor process_document_text "FACTUUR\nFactuurnummer: INV-001\nTotaal: €1000"
```

## 🛠️ Beschikbare Tools

De MCP server biedt de volgende tools:

| Tool | Beschrijving | Gebruik |
|------|---------------|---------|
| `process_document_text` | Verwerk document tekst | `/mcp-invoice-processor process_document_text "tekst"` |
| `process_document_file` | Verwerk document bestand | `/mcp-invoice-processor process_document_file "pad/naar/bestand"` |
| `classify_document_type` | Classificeer document type | `/mcp-invoice-processor classify_document_type "tekst"` |
| `get_metrics` | Haal metrics op | `/mcp-invoice-processor get_metrics` |
| `health_check` | Server health check | `/mcp-invoice-processor health_check` |

## 🔍 Troubleshooting

### Probleem: MCP server niet gevonden
**Oplossing:**
1. Controleer of `mcp.json` in de juiste directory staat
2. Herstart Cursor volledig
3. Controleer of de paden in `mcp.json` correct zijn

### Probleem: Ollama verbinding mislukt
**Oplossing:**
1. Start Ollama server: `ollama serve`
2. Controleer of Ollama draait op `localhost:11434`
3. Test met: `ollama list`

### Probleem: Module niet gevonden
**Oplossing:**
1. Installeer dependencies: `uv sync --dev`
2. Controleer of `src/mcp_invoice_processor/` bestaat
3. Test lokaal: `uv run python -m src.mcp_invoice_processor.fastmcp_server`

### Probleem: Permission denied
**Oplossing:**
1. Controleer of `uv.exe` pad correct is
2. Controleer of je schrijfrechten hebt in de project directory
3. Probeer Cursor als administrator te starten

## 📊 Monitoring

De MCP server bevat uitgebreide monitoring:

```bash
# Start monitoring dashboard
uv run python -m src.mcp_invoice_processor.monitoring.dashboard

# Dashboard beschikbaar op: http://localhost:8000
```

## 🎯 Volgende Stappen

Na succesvolle activatie:

1. **Test met echte documenten**: Upload PDF's en test de verwerking
2. **Pas configuratie aan**: Wijzig Ollama model of timeout waarden
3. **Integreer in workflows**: Gebruik de tools in je dagelijkse werk
4. **Monitor prestaties**: Gebruik de metrics dashboard

## 📚 Meer Informatie

- [FastMCP Documentatie](https://gofastmcp.com/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Cursor MCP Integratie](https://cursor.sh/docs/mcp)

## 🆘 Support

Als je problemen ondervindt:

1. Check de troubleshooting sectie hierboven
2. Controleer de Cursor logs
3. Test de server lokaal: `python test_cursor_mcp.py`
4. Raadpleeg de project documentatie

---

**🎉 Succesvol geactiveerd?** Test dan met een eenvoudig commando:
```bash
/mcp-invoice-processor health_check
```

Je zou een health status moeten zien met Ollama connectiviteit informatie.
