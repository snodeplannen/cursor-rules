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
    - Automatische document classificatie via processor registry
    - Gestructureerde data extractie met Ollama LLM
    - Uitgebreide metrics en monitoring
    - Multi-format ondersteuning (TXT, PDF)
    
    🔧 Beschikbare Tools:
    - process_document_text(text, extraction_method): Verwerk document tekst
    - process_document_file(file_path, extraction_method): Verwerk document bestand
    - classify_document_type(text): Classificeer document type
    - get_metrics(): Haal server metrics op
    - health_check(): Controleer server status
    - Processor-specifieke tools: Dynamisch gegenereerd op basis van beschikbare processors
    
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

# Registreer processor-specifieke tools dynamisch
from .processors import get_registry
from .tools import _init_processors  # Zorg dat processors zijn geregistreerd

def register_processor_tools():
    """Registreer dynamisch tools voor alle beschikbare processors."""
    # Zorg dat processors zijn geïnitialiseerd
    _init_processors()
    
    registry = get_registry()
    processors = registry.get_all_processors()
    
    for processor in processors:
        # Maak een dynamische tool functie voor deze processor
        async def create_processor_tool(proc):
            async def processor_tool(text: str, extraction_method: str = "hybrid", model: str | None = None) -> dict[str, any]:
                """
                {proc.display_name} document processor.
                
                {proc.tool_description}
                
                Args:
                    text: Document tekst om te verwerken
                    extraction_method: Extractie methode ("hybrid", "json_schema", "prompt_parsing")
                    model: Ollama model naam (optioneel)
                
                Returns:
                    Dict met geëxtraheerde {proc.document_type} data
                """
                return await tools.process_document_text(text, extraction_method, model)
            
            # Update functie metadata voor FastMCP
            processor_tool.__name__ = proc.tool_name
            processor_tool.__doc__ = processor_tool.__doc__.format(
                proc=proc,
                proc_display_name=proc.display_name,
                proc_tool_description=proc.tool_description,
                proc_document_type=proc.document_type
            )
            
            return processor_tool
        
        # Registreer de tool met metadata
        tool_func = create_processor_tool(processor)
        
        # Gebruik processor metadata voor FastMCP registratie
        metadata = processor.tool_metadata
        mcp.tool(
            name=metadata["name"],
            description=metadata["description"],
            annotations=metadata["annotations"]
        )(tool_func)
        
        logger.info(f"✅ Geregistreerd: {processor.tool_name} - {processor.display_name}")
        logger.debug(f"   Metadata: {metadata}")

# Registreer alle processor tools
register_processor_tools()


# Resources voor documentatie en voorbeelden
@mcp.resource("mcp://document-types")
async def document_types_examples() -> str:
    """Dynamisch gegenereerde voorbeelden van ondersteunde document types."""
    # Zorg dat processors zijn geïnitialiseerd
    _init_processors()
    
    registry = get_registry()
    processors = registry.get_all_processors()
    
    # Genereer dynamische documentatie
    docs = ["# 📋 Ondersteunde Document Types\n"]
    
    for processor in processors:
        examples = processor.tool_examples
        
        docs.append(f"## {examples['emoji']} {processor.display_name}")
        docs.append(f"- **Tool naam**: `{processor.tool_name}`")
        docs.append(f"- **Trefwoorden**: {', '.join(examples['keywords'][:10])}{'...' if len(examples['keywords']) > 10 else ''}")
        docs.append("- **Geëxtraheerde velden**:")
        
        for field in examples['extracted_fields']:
            docs.append(f"  - {field}")
        
        docs.append(f"- **Ondersteunde methoden**: {', '.join(examples['supported_methods'])}")
        docs.append(f"- **Ondersteunde formaten**: {', '.join(examples['supported_formats'])}")
        
        docs.append("- **Voorbeeld document**:")
        docs.append("  ```")
        docs.append(f"  {examples['example_text']}")
        docs.append("  ```")
        
        docs.append("- **Voorbeeld gebruik**:")
        docs.append("  ```python")
        docs.append(f"  {examples['usage_example']}")
        docs.append("  ```")
        
        docs.append("")  # Lege regel tussen processors
    
    docs.append("## 🔧 Algemene Tools")
    docs.append("- `process_document_text` - Automatische document type detectie")
    docs.append("- `process_document_file` - Verwerk bestanden (PDF, TXT)")
    docs.append("- `classify_document_type` - Alleen classificatie zonder extractie")
    docs.append("- `get_metrics` - Systeem statistieken")
    docs.append("- `health_check` - Service health status")
    
    return "\n".join(docs)

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
    """Dynamisch gegenereerde gids voor document verwerking."""
    
    # Zorg dat processors zijn geïnitialiseerd
    _init_processors()
    
    registry = get_registry()
    processors = registry.get_all_processors()
    
    # Als specifiek document type gevraagd wordt
    if document_type.lower() != "any":
        for processor in processors:
            if processor.document_type.lower() == document_type.lower():
                examples = processor.tool_examples
                
                guide = f"""
# {examples['emoji']} {processor.display_name} Verwerking Gids

## 🎯 Optimale {processor.display_name} Verwerking:
1. **Structuur**: Zorg voor duidelijke secties en consistente formatting
2. **Inhoud**: Include alle relevante informatie voor dit documenttype
3. **Taal**: Ondersteunt Nederlands en Engels
4. **Formaat**: Gebruik consistente datum- en nummerformaten

## 🔧 Aanbevolen Methoden:
- **Hybrid**: Voor de meeste {processor.document_type} documenten (combineert structuur met flexibiliteit)
- **JSON Schema**: Voor gestructureerde documenten met vaste formaten
- **Prompt Parsing**: Voor complexe of ongestructureerde documenten

## 💡 Voorbeeld Gebruik:
```python
{examples['usage_example']}
```

## 📋 Geëxtraheerde Velden:
"""
                for field in examples['extracted_fields']:
                    guide += f"- {field}\n"
                
                guide += f"""
## 🔍 Trefwoorden voor Detectie:
{', '.join(examples['keywords'][:15])}{'...' if len(examples['keywords']) > 15 else ''}

## 📄 Voorbeeld Document:
```
{examples['example_text']}
```
"""
                return guide
        
        # Document type niet gevonden
        return f"❌ Document type '{document_type}' niet gevonden. Beschikbare types: {', '.join([p.document_type for p in processors])}"
    
    # Algemene gids voor alle document types
    guide = """
# 📋 Document Verwerking Gids

## 🎯 Algemene Richtlijnen:
1. **Structuur**: Zorg voor duidelijke secties en consistente formatting
2. **Inhoud**: Include alle relevante informatie voor het documenttype
3. **Taal**: Ondersteunt Nederlands en Engels
4. **Formaat**: Gebruik consistente datum- en nummerformaten

## 🔧 Extractie Methoden:
- **Hybrid**: Aanbevolen voor de meeste documenten (combineert precisie met flexibiliteit)
- **JSON Schema**: Voor gestructureerde documenten met vaste formaten
- **Prompt Parsing**: Voor complexe of ongestructureerde documenten

## 📊 Beschikbare Document Types:
"""
    
    for processor in processors:
        examples = processor.tool_examples
        guide += f"\n### {examples['emoji']} {processor.display_name}\n"
        guide += f"- **Tool**: `{processor.tool_name}`\n"
        guide += f"- **Trefwoorden**: {', '.join(examples['keywords'][:8])}{'...' if len(examples['keywords']) > 8 else ''}\n"
        guide += f"- **Velden**: {len(examples['extracted_fields'])} geëxtraheerde velden\n"
    
    guide += """
## 💡 Algemene Tools:
- `process_document_text` - Automatische document type detectie
- `process_document_file` - Verwerk bestanden (PDF, TXT)
- `classify_document_type` - Alleen classificatie zonder extractie
- `get_metrics` - Systeem statistieken
- `health_check` - Service health status

## 🚀 Gebruik Tips:
1. Gebruik `hybrid` methode voor beste resultaten
2. Voor grote documenten wordt automatisch chunking toegepast
3. Alle tools ondersteunen optionele model parameter voor Ollama model selectie
4. Document type wordt automatisch gedetecteerd op basis van keywords
"""
    
    return guide

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
        logger.info("🚀 Starting MCP Document Processor Server...")
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
    import sys
    
    # Ondersteun --help parameter
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("MCP Document Processor Server")
        print("Usage: mcp-server [--help]")
        print("")
        print("This server runs in STDIO transport mode for MCP communication.")
        print("It provides document processing tools with dynamic processor support.")
        print("")
        print("Available tools:")
        print("  - process_document_text: Process document text")
        print("  - process_document_file: Process document file")
        print("  - classify_document_type: Classify document type")
        print("  - get_metrics: Get server metrics")
        print("  - health_check: Check server health")
        print("  - Processor-specific tools: Dynamically generated based on available processors")
        sys.exit(0)
    
    run_server()
