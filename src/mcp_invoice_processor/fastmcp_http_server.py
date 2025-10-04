#!/usr/bin/env python3
"""
FastMCP HTTP Server voor document verwerking met Ollama integratie.
HTTP transport versie van de MCP Document Processor.
"""

import logging
import warnings
import sys
from pathlib import Path

# Voeg src directory toe aan Python path voor standalone execution
if __name__ == "__main__":
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

# Onderdruk alle output tijdens import om JSON communicatie niet te verstoren
import io
_stdout = sys.stdout
sys.stdout = io.StringIO()

from fastmcp import FastMCP  # noqa: E402
from mcp_invoice_processor.config import settings  # noqa: E402
from mcp_invoice_processor.logging_config import setup_logging  # noqa: E402
from mcp_invoice_processor import tools  # noqa: E402

# Onderdruk DeprecationWarnings van externe libraries
warnings.filterwarnings("ignore", category=DeprecationWarning, module="fitz")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="swigobject")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="swigvarlink")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sys")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="builtins")

# Onderdruk alle DeprecationWarnings globaal
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Setup logging met de juiste configuratie
logger = setup_logging(log_level="INFO")

# Herstel stdout na logging setup
sys.stdout = _stdout

# Initialize FastMCP server met HTTP transport
mcp = FastMCP(
    name="MCP Document Processor HTTP",
    instructions="""
    Deze MCP server biedt geavanceerde document verwerking met AI-powered extractie via HTTP transport.
    
    🎯 Hoofdfunctionaliteit:
    - Automatische document classificatie (CV, Factuur, etc.)
    - Gestructureerde data extractie met Ollama LLM
    - Uitgebreide metrics en monitoring
    - Multi-format ondersteuning (TXT, PDF)
    - HTTP transport voor web integratie
    
    🔧 Beschikbare Tools:
    - process_document_text(text, extraction_method): Verwerk document tekst
    - process_document_file(file_path, extraction_method): Verwerk document bestand
    - classify_document_type(text): Classificeer document type
    - get_metrics(): Haal server metrics op
    - health_check(): Controleer server status
    
    📊 Extractie Methodes:
    - "hybrid": Combinatie van JSON schema en prompt parsing (aanbevolen)
    - "json_schema": Gestructureerde extractie met JSON schema
    - "prompt_parsing": Flexibele extractie met prompt engineering
    
    🌐 HTTP Transport:
    - Server draait op HTTP transport
    - Beschikbaar via HTTP endpoints
    - Ondersteunt streaming responses
    - Compatibel met web applicaties
    
    💡 Tips:
    - Gebruik "hybrid" methode voor beste resultaten
    - Voor grote documenten: gebruik process_document_file
    - Controleer altijd eerst de health_check voor Ollama connectie
    """,
    on_duplicate_tools="warn"
)

# Registreer de gedeelde tools
mcp.tool()(tools.process_document_text)
mcp.tool()(tools.process_document_file)
mcp.tool()(tools.classify_document_type)
mcp.tool()(tools.get_metrics)
mcp.tool()(tools.health_check)

# Resources voor documentatie en voorbeelden
@mcp.resource("mcp://document-types")
async def document_types_examples() -> str:
    """Voorbeelden van ondersteunde document types."""
    return """
    # 📋 Ondersteunde Document Types
    
    ## 👤 CV/Resume
    - **Trefwoorden**: ervaring, opleiding, vaardigheden, curriculum vitae, werkervaring
    - **Geëxtraheerde velden**: naam, email, telefoon, werkervaring, opleiding, vaardigheden
    - **Voorbeeld gebruik**: 
      ```
      result = await process_document_text(cv_text, "hybrid")
      print(f"Naam: {result['full_name']}")
      ```
    
    ## 🧾 Factuur/Invoice  
    - **Trefwoorden**: factuur, totaal, bedrag, btw, klant, leverancier
    - **Geëxtraheerde velden**: factuurnummer, bedragen, datum, bedrijfsinformatie
    - **Voorbeeld gebruik**:
      ```
      result = await process_document_text(invoice_text, "json_schema")
      print(f"Totaal: €{result['total_amount']}")
      ```
    
    ## 🚀 Gebruik
    1. **Tekst verwerking**: `process_document_text(text, method)`
    2. **Bestand verwerking**: `process_document_file(path, method)`  
    3. **Alleen classificatie**: `classify_document_type(text)`
    4. **Status check**: `health_check()` - controleer Ollama connectie
    """

def run_http_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start de FastMCP server in HTTP transport mode."""
    try:
        # Configureer MCP server logging
        logger.info("🚀 Starting MCP Document Processor HTTP Server...")
        logger.info(f"📊 Ollama host: {settings.ollama.HOST}")
        logger.info(f"🤖 Ollama model: {settings.ollama.MODEL}")
        logger.info(f"🌐 HTTP transport: {host}:{port}")
        logger.info(f"🔗 MCP endpoint: http://{host}:{port}/mcp/")
        
        # Configureer MCP server logging
        mcp_server_logger = logging.getLogger("mcp_server_integration")
        mcp_server_logger.info("🔄 MCP HTTP server configuratie voltooid")
        mcp_server_logger.info("📋 Server gereed voor HTTP transport")
        
        # Start de server in HTTP transport mode
        logger.info("🔄 Starting MCP server in HTTP transport mode...")
        mcp_server_logger.info("🚀 MCP HTTP server starten...")
        
        # Start FastMCP server met HTTP transport (volgens FastMCP docs)
        mcp.run(
            transport="http",
            host=host,
            port=port
        )
        
    except Exception as e:
        logger.error(f"Fout bij starten MCP HTTP server: {e}", exc_info=True)
        raise

async def run_http_server_async(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start de FastMCP server asynchroon in HTTP transport mode."""
    try:
        logger.info(f"🚀 Starting MCP HTTP server (async) on {host}:{port}")
        logger.info(f"🔗 MCP endpoint: http://{host}:{port}/mcp/")
        
        # Start FastMCP server asynchroon met HTTP transport (volgens FastMCP docs)
        await mcp.run_async(
            transport="http",
            host=host,
            port=port
        )
        
    except Exception as e:
        logger.error(f"Fout bij starten MCP HTTP server (async): {e}", exc_info=True)
        raise

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments (volgens FastMCP docs: default 127.0.0.1:8000)
    host = "127.0.0.1"
    port = 8000
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    run_http_server(host, port)
