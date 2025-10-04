#!/usr/bin/env python3
"""
FastMCP Server voor document verwerking met Ollama integratie.
Gebaseerd op de Scrapfly MCP guide: https://scrapfly.io/blog/posts/how-to-build-an-mcp-server-in-python-a-complete-guide
"""

import logging
import warnings
import sys
import os

# Onderdruk alle output tijdens import om JSON communicatie niet te verstoren
import io
_stdout = sys.stdout
sys.stdout = io.StringIO()

# Add src to path before other imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

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

# Setup logging met de juiste configuratie (zonder console output)
logger = setup_logging(log_level="INFO")

# Herstel stdout na logging setup
sys.stdout = _stdout

# Onderdruk FastMCP banner output
os.environ['FASTMCP_DISABLE_BANNER'] = '1'

# Zet Python logging level om DEBUG output te voorkomen
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("mcp").setLevel(logging.WARNING)
logging.getLogger("mcp.server").setLevel(logging.WARNING)
logging.getLogger("mcp.server.lowlevel").setLevel(logging.WARNING)
logging.getLogger("fastmcp").setLevel(logging.WARNING)

# Initialize FastMCP server met uitgebreide instructies
mcp = FastMCP(
    name="MCP Document Processor",
    instructions="""
    Deze MCP server biedt geavanceerde document verwerking met AI-powered extractie.
    
    🎯 Hoofdfunctionaliteit:
    - Automatische document classificatie (CV, Factuur, etc.)
    - Gestructureerde data extractie met Ollama LLM
    - Uitgebreide metrics en monitoring
    - Multi-format ondersteuning (TXT, PDF)
    
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
    
    💡 Tips:
    - Gebruik "hybrid" methode voor beste resultaten
    - Voor grote documenten: gebruik process_document_file
    - Controleer altijd eerst de health_check voor Ollama connectie
    """,
    on_duplicate_tools="warn"
)

# Configureer MCP server logging om Cursor MCP logs te verbeteren
def on_startup():
    """Wordt uitgevoerd wanneer de MCP server start."""
    try:
        logger.info("🚀 MCP Document Processor Server gestart")
        logger.info("📊 Server gereed voor document verwerking")
        logger.info("🔧 Beschikbare tools: process_document_text, process_document_file, classify_document_type, get_metrics, health_check")
        
        # Gebruik speciale MCP server logger
        mcp_server_logger = logging.getLogger("mcp_server_integration")
        mcp_server_logger.info("✅ MCP server startup voltooid")
        mcp_server_logger.info("🔗 Server verbonden met Cursor")
        
    except Exception as e:
        logger.error(f"Fout tijdens MCP server startup: {e}", exc_info=True)

def on_shutdown():
    """Wordt uitgevoerd wanneer de MCP server stopt."""
    try:
        logger.info("🛑 MCP Document Processor Server gestopt")
        
        # Gebruik speciale MCP server logger
        mcp_server_logger = logging.getLogger("mcp_server_integration")
        mcp_server_logger.info("🔄 MCP server shutdown voltooid")
        
    except Exception as e:
        logger.error(f"Fout tijdens MCP server shutdown: {e}", exc_info=True)


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

@mcp.resource("mcp://extraction-methods")
async def extraction_methods_guide() -> str:
    """Gids voor extractie methodes."""
    return """
    # 🔧 Extractie Methodes Gids
    
    ## 🎯 Hybrid (Aanbevolen)
    - **Wanneer**: Voor de meeste documenten
    - **Voordelen**: Combineert precisie van JSON schema met flexibiliteit van prompts
    - **Gebruik**: `extraction_method="hybrid"`
    
    ## 📊 JSON Schema  
    - **Wanneer**: Voor gestructureerde documenten met vaste formaten
    - **Voordelen**: Hoge precisie, consistente output
    - **Gebruik**: `extraction_method="json_schema"`
    
    ## 💬 Prompt Parsing
    - **Wanneer**: Voor complexe of ongestructureerde documenten
    - **Voordelen**: Flexibel, kan complexe patronen herkennen
    - **Gebruik**: `extraction_method="prompt_parsing"`
    
    ## 🎨 Best Practices
    1. Start altijd met "hybrid" methode
    2. Gebruik "json_schema" voor facturen en gestructureerde data
    3. Gebruik "prompt_parsing" voor complexe CV's of vrije tekst
    4. Test verschillende methodes voor optimale resultaten
    """

@mcp.resource("mcp://server-config")
async def server_configuration() -> str:
    """Server configuratie informatie."""
    return f"""
    # ⚙️ Server Configuratie
    
    ## 🤖 Ollama Integratie
    - **Host**: {settings.ollama.HOST}
    - **Model**: {settings.ollama.MODEL}
    - **Timeout**: {settings.ollama.TIMEOUT}s
    
    ## 📊 Monitoring
    - **Metrics**: Uitgebreide performance metrics beschikbaar
    - **Logging**: Gestructureerde logging met verschillende niveaus
    - **Health Checks**: Automatische Ollama connectie monitoring
    
    ## 🔧 Ondersteunde Formaten
    - **Tekst**: Direct tekst input via process_document_text
    - **PDF**: Automatische tekst extractie via process_document_file
    - **TXT**: Plain text bestanden
    
    ## 🚀 Performance Tips
    - Gebruik kleinere documenten voor snellere verwerking
    - Monitor metrics voor performance optimalisatie
    - Controleer Ollama status via health_check
    """


# Prompts voor document verwerking instructies
@mcp.prompt("document-processing-guide")
async def document_processing_guide(document_type: str = "any") -> str:
    """Gids voor document verwerking met specifieke instructies per type."""
    
    if document_type.lower() == "cv":
        return """
        # 👤 CV Verwerking Gids
        
        ## 🎯 Optimale CV Verwerking:
        1. **Structuur**: Zorg voor duidelijke secties (Persoonlijke gegevens, Werkervaring, Opleiding)
        2. **Datums**: Gebruik consistente datumformaten (DD-MM-YYYY of MM/YYYY)
        3. **Vaardigheden**: Lijst vaardigheden duidelijk op, gescheiden door komma's
        4. **Contact**: Include contactinformatie bovenaan het document
        5. **Taal**: Ondersteunt Nederlands en Engels
        
        ## 🔧 Aanbevolen Methode:
        - **Hybrid**: Voor de meeste CV's (combineert structuur met flexibiliteit)
        - **Prompt Parsing**: Voor creatieve of ongestructureerde CV's
        
        ## 💡 Voorbeeld Gebruik:
        ```python
        result = await process_document_text(cv_text, "hybrid")
        print(f"👤 Naam: {result['full_name']}")
        print(f"📧 Email: {result['email']}")
        print(f"💼 Ervaring: {len(result['work_experience'])} posities")
        ```
        """
    elif document_type.lower() == "invoice":
        return """
        # 🧾 Factuur Verwerking Gids
        
        ## 🎯 Optimale Factuur Verwerking:
        1. **Factuurnummer**: Zorg voor duidelijk zichtbaar factuurnummer
        2. **Datums**: Include factuurdatum en vervaldatum
        3. **Bedragen**: Lijst alle regels met bedragen en BTW
        4. **BTW**: Toon BTW berekening en percentage
        5. **Bedrijfsinfo**: Include leverancier en klant informatie
        6. **Totaal**: Duidelijk eindtotaal inclusief BTW
        
        ## 🔧 Aanbevolen Methode:
        - **JSON Schema**: Voor gestructureerde facturen (aanbevolen)
        - **Hybrid**: Voor complexere factuurformaten
        
        ## 💡 Voorbeeld Gebruik:
        ```python
        result = await process_document_text(invoice_text, "json_schema")
        print(f"🧾 Nummer: {result['invoice_number']}")
        print(f"💰 Totaal: €{result['total_amount']}")
        print(f"📅 Datum: {result['invoice_date']}")
        ```
        """
    else:
        return """
        # 📄 Algemene Document Verwerking Gids
        
        ## 🎯 Ondersteunde Document Types:
        - **👤 CV/Resume**: Persoonlijke en professionele informatie
        - **🧾 Factuur/Invoice**: Financiële transactie documenten
        - **📄 Algemeen**: Automatische classificatie voor onbekende types
        
        ## 🔄 Verwerkingsstappen:
        1. **📊 Classificatie**: Automatische detectie van document type
        2. **📝 Extractie**: Tekst extractie (PDF → tekst indien nodig)
        3. **🤖 AI Verwerking**: Gestructureerde data extractie met Ollama
        4. **✅ Validatie**: Data validatie en opschoning
        5. **📤 Output**: Gestructureerde JSON output
        
        ## 🚀 Snelstart:
        ```python
        # Voor tekst
        result = await process_document_text(text, "hybrid")
        
        # Voor bestanden  
        result = await process_document_file("document.pdf", "hybrid")
        
        # Alleen classificatie
        doc_type = await classify_document_type(text)
        ```
        
        ## 💡 Tips:
        - Start altijd met `health_check()` om Ollama connectie te verifiëren
        - Gebruik `get_metrics()` voor performance monitoring
        - Probeer verschillende extractie methodes voor optimale resultaten
        """

@mcp.prompt("troubleshooting-guide") 
async def troubleshooting_guide(issue_type: str = "general") -> str:
    """Troubleshooting gids voor veelvoorkomende problemen."""
    
    if issue_type.lower() == "ollama":
        return """
        # 🔧 Ollama Troubleshooting
        
        ## ❌ Veelvoorkomende Problemen:
        
        ### 1. Ollama Connectie Mislukt
        - **Symptoom**: "Ollama connectie mislukt" in health_check
        - **Oplossing**: 
          - Controleer of Ollama draait: `ollama serve`
          - Verificeer host configuratie in settings
          - Test connectie: `curl http://localhost:11434/api/tags`
        
        ### 2. Model Niet Beschikbaar
        - **Symptoom**: Model niet gevonden error
        - **Oplossing**:
          - Download model: `ollama pull llama3.2`
          - Controleer beschikbare modellen: `ollama list`
          - Update MODEL setting in configuratie
        
        ### 3. Timeout Errors
        - **Symptoom**: Request timeout tijdens verwerking
        - **Oplossing**:
          - Verhoog TIMEOUT setting
          - Gebruik kleinere documenten
          - Controleer Ollama performance
        
        ## ✅ Health Check:
        ```python
        result = await health_check()
        print(f"Status: {result['status']}")
        print(f"Ollama: {result['ollama_status']}")
        ```
        """
    else:
        return """
        # 🛠️ Algemene Troubleshooting
        
        ## 🔍 Diagnostiek Stappen:
        1. **Health Check**: `await health_check()` - controleer server status
        2. **Metrics**: `await get_metrics()` - bekijk performance data  
        3. **Logs**: Controleer logs voor error details
        4. **Ollama**: Verificeer Ollama connectie en model beschikbaarheid
        
        ## ❌ Veelvoorkomende Problemen:
        
        ### Document Verwerking Mislukt
        - Controleer document formaat (TXT/PDF ondersteund)
        - Probeer verschillende extractie methodes
        - Verificeer document grootte (< 1MB aanbevolen)
        
        ### Lage Extractie Kwaliteit  
        - Gebruik "hybrid" methode voor beste resultaten
        - Controleer document kwaliteit en structuur
        - Probeer verschillende Ollama modellen
        
        ### Performance Problemen
        - Monitor metrics voor bottlenecks
        - Optimaliseer Ollama configuratie
        - Gebruik kleinere batch sizes
        
        ## 🆘 Support:
        - Controleer logs in `/logs` directory
        - Gebruik `get_metrics()` voor performance data
        - Test met `health_check()` voor system status
        """


def run_server():
    """Start de FastMCP server."""
    try:
        # Configureer MCP server logging
        logger.info("🚀 Starting MCP Invoice Processor Server...")
        logger.info(f"📊 Ollama host: {settings.ollama.HOST}")
        logger.info(f"🤖 Ollama model: {settings.ollama.MODEL}")
        
        # Configureer MCP server logging om Cursor MCP logs te verbeteren
        mcp_server_logger = logging.getLogger("mcp_server_integration")
        mcp_server_logger.info("🔄 MCP server configuratie voltooid")
        mcp_server_logger.info("📋 Server gereed voor Cursor integratie")
        
        # Run the server op STDIO transport
        logger.info("🔄 Starting MCP server on STDIO transport...")
        mcp_server_logger.info("🚀 MCP server starten...")
        
        # Redirect stderr to null to prevent any debug output
        if os.name == 'nt':  # Windows
            devnull = open('nul', 'w')
        else:  # Unix/Linux
            devnull = open('/dev/null', 'w')
        
        old_stderr = sys.stderr
        sys.stderr = devnull
        
        try:
            # Start de server zonder extra logging om Cursor MCP logs te vermijden
            mcp.run()
        finally:
            # Restore stderr
            sys.stderr = old_stderr
            devnull.close()
        
    except Exception as e:
        logger.error(f"Fout bij starten MCP server: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run_server()
