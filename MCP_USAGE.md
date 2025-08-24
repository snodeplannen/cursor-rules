# MCP Invoice Processor - Gebruikshandleiding

## 📋 Overzicht

Deze handleiding legt uit hoe je de MCP Invoice Processor kunt gebruiken met verschillende MCP clients en configuraties.

## 🚀 Snelle Start

### 1. STDIO Transport (Aanbevolen voor lokale ontwikkeling)

Gebruik de `mcp.json` configuratie:

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
        "src.mcp_invoice_processor.main"
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

**Let op**: Pas de paden aan naar jouw systeem:
- `command`: Absolute pad naar uv executable
- `--directory`: Absolute pad naar je project directory

### 2. HTTP Transport (Voor netwerk toegang)

Gebruik de `mcp-http.json` configuratie:

```json
{
  "mcpServers": {
    "mcp-invoice-processor-http": {
      "command": "C:\\ProgramData\\miniforge3\\Scripts\\uv.exe",
      "args": [
        "--directory",
        "C:\\py_cursor-rules\\cursor_ratsenbergertest\\",
        "run",
        "fastmcp",
        "run",
        "src.mcp_invoice_processor.main:mcp",
        "--host",
        "127.0.0.1",
        "--port",
        "8080",
        "--transport",
        "http"
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

**Let op**: Pas de paden aan naar jouw systeem:
- `command`: Absolute pad naar uv executable
- `--directory`: Absolute pad naar je project directory

## 🔧 Configuratie Opties

### Omgevingsvariabelen

| Variabele | Beschrijving | Standaard | Vereist |
|-----------|---------------|-----------|---------|
| `LOG_LEVEL` | Logging niveau | `INFO` | Nee |
| `OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` | Ja |
| `OLLAMA_MODEL` | LLM model naam | `llama3` | Ja |
| `OLLAMA_TIMEOUT` | Timeout in seconden | `120` | Nee |

### Transport Opties

#### STDIO Transport
- **Voordelen**: Eenvoudig, geen netwerk configuratie nodig
- **Gebruik**: Ideaal voor lokale ontwikkeling en CLI tools
- **Configuratie**: Gebruik `mcp.json`

#### HTTP Transport
- **Voordelen**: Netwerk toegankelijk, kan door meerdere clients worden gebruikt
- **Gebruik**: Ideaal voor web applicaties en remote clients
- **Configuratie**: Gebruik `mcp-http.json`

## 📱 MCP Client Integratie

### Met Cursor/VS Code

1. **Installeer de MCP extension** in VS Code
2. **Kopieer de configuratie** naar je workspace
3. **Herstart VS Code** om de MCP server te laden
4. **Gebruik de tools** via de MCP interface

### Met andere MCP Clients

#### Python Client
```python
import mcp

# Verbind met de server
client = mcp.ClientStdio(
    ["C:\\ProgramData\\miniforge3\\Scripts\\uv.exe", "--directory", "C:\\py_cursor-rules\\cursor_ratsenbergertest\\", "run", "python", "-m", "src.mcp_invoice_processor.main"]
)

# Gebruik de process_document tool
result = await client.call_tool(
    "process_document",
    {
        "file_content_base64": "base64_encoded_pdf_content",
        "file_name": "document.pdf"
    }
)
```

#### JavaScript/TypeScript Client
```typescript
import { Client } from '@modelcontextprotocol/sdk/client';

// Verbind met de server
const client = new Client(
    ['C:\\ProgramData\\miniforge3\\Scripts\\uv.exe', '--directory', 'C:\\py_cursor-rules\\cursor_ratsenbergertest\\', 'run', 'python', '-m', 'src.mcp_invoice_processor.main'],
    'stdio'
);

// Gebruik de process_document tool
const result = await client.callTool('process_document', {
    file_content_base64: 'base64_encoded_pdf_content',
    file_name: 'document.pdf'
});
```

## 🛠️ Beschikbare Tools

### `process_document`

Verwerkt een PDF-document en extraheert gestructureerde data.

**Parameters:**
- `file_content_base64` (string): Base64-gecodeerde PDF-inhoud
- `file_name` (string): Naam van het bestand

**Returns:**
```json
{
  "document_type": "cv|invoice|unknown",
  "data": {
    // Gestructureerde data volgens documenttype
  },
  "status": "success|error",
  "error_message": "Foutmelding indien van toepassing"
}
```

## 🔍 Voorbeelden

### CV Verwerking
```bash
# Start de server
uv run python -m src.mcp_invoice_processor.main

# In een andere terminal, gebruik de MCP client
curl -X POST http://127.0.0.1:8080/mcp/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "process_document",
      "arguments": {
        "file_content_base64": "JVBERi0xLjQK...",
        "file_name": "cv.pdf"
      }
    }
  }'
```

### Factuur Verwerking
```bash
# Gebruik de HTTP transport configuratie
uv run fastmcp run src.mcp_invoice_processor.main:mcp --host 127.0.0.1 --port 8080 --transport http

# De server is nu beschikbaar op http://127.0.0.1:8080/mcp/
```

## 🐛 Troubleshooting

### Veelvoorkomende Problemen

1. **"File not found" error**
   - Controleer of je in de juiste directory bent
   - Verifieer dat alle bestanden bestaan

2. **Ollama verbindingsfout**
   - Controleer of Ollama draait op `localhost:11434`
   - Verifieer de `OLLAMA_HOST` configuratie

3. **Port al in gebruik**
   - Verander de poort in de configuratie
   - Stop andere services die de poort gebruiken

4. **Import errors**
   - Voer `uv sync --dev` uit om dependencies te installeren
   - Controleer of alle Python bestanden correct zijn aangemaakt

### Debug Modus

Voor uitgebreide logging, stel `LOG_LEVEL=DEBUG` in:

```json
{
  "env": {
    "LOG_LEVEL": "DEBUG"
  }
}
```

## 📚 Meer Informatie

- [MCP Protocol Specificatie](https://modelcontextprotocol.io/)
- [FastMCP Documentatie](https://gofastmcp.com/)
- [Ollama Documentatie](https://ollama.ai/docs)

## 🤝 Ondersteuning

Voor vragen of problemen:
1. Controleer de logs met `LOG_LEVEL=DEBUG`
2. Verifieer de configuratie
3. Test met een eenvoudige PDF eerst
4. Controleer of Ollama correct is geconfigureerd
