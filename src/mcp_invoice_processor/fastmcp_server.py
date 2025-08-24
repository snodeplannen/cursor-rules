#!/usr/bin/env python3
"""
FastMCP Server voor document verwerking met Ollama integratie.
Gebaseerd op de Scrapfly MCP guide: https://scrapfly.io/blog/posts/how-to-build-an-mcp-server-in-python-a-complete-guide
"""

import logging
import warnings
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Onderdruk alle output tijdens import om JSON communicatie niet te verstoren
import io
_stdout = sys.stdout
sys.stdout = io.StringIO()

# Add src to path before other imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastmcp import FastMCP, Context  # noqa: E402
from mcp_invoice_processor.processing.pipeline import extract_structured_data, ExtractionMethod  # noqa: E402
from mcp_invoice_processor.processing.classification import classify_document, DocumentType  # noqa: E402
from mcp_invoice_processor.processing.models import CVData, InvoiceData  # noqa: E402
from mcp_invoice_processor.config import settings  # noqa: E402
from mcp_invoice_processor.monitoring.metrics import metrics_collector  # noqa: E402
from mcp_invoice_processor.logging_config import setup_logging  # noqa: E402

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

# Initialize FastMCP server
mcp = FastMCP("MCP Invoice Processor")

# Configureer MCP server logging om Cursor MCP logs te verbeteren
def on_startup():
    """Wordt uitgevoerd wanneer de MCP server start."""
    try:
        logger.info("🚀 MCP Invoice Processor Server gestart")
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
        logger.info("🛑 MCP Invoice Processor Server gestopt")
        
        # Gebruik speciale MCP server logger
        mcp_server_logger = logging.getLogger("mcp_server_integration")
        mcp_server_logger.info("🔄 MCP server shutdown voltooid")
        
    except Exception as e:
        logger.error(f"Fout tijdens MCP server shutdown: {e}", exc_info=True)


@mcp.tool()
async def process_document_text(text: str, ctx: Context, extraction_method: str = "hybrid") -> Dict[str, Any]:
    """
    Verwerk document tekst en extraheer gestructureerde data.
    
    Args:
        text: De tekst inhoud van het document
        ctx: FastMCP context voor logging en progress
        extraction_method: Extractie methode - "hybrid" (default), "json_schema" of "prompt_parsing"
    
    Returns:
        Dict met geëxtraheerde document data
    """
    try:
        # Onderdruk warnings tijdens document verwerking
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            # Converteer string parameter naar enum
            try:
                method_enum = ExtractionMethod(extraction_method.lower())
            except ValueError:
                method_enum = ExtractionMethod.HYBRID
                logger.warning(f"Onbekende extractie methode '{extraction_method}', gebruik HYBRID als default")
            
            # Log input parameters voor troubleshooting
            logger.info(f"process_document_text aangeroepen met tekst lengte: {len(text)} karakters, methode: {method_enum.value}")
            logger.debug(f"Tekst preview: {text[:200]}...")
            
            method_name = "JSON Schema Mode" if method_enum == ExtractionMethod.JSON_SCHEMA else "Prompt Parsing Mode"
            await ctx.info(f"🚀 Starten document verwerking ({method_name})...")
            
            # Start metrics timer
            metrics_collector.start_timer("document_processing")
            
            # Classificeer document type
            await ctx.info("📊 Classificeren document type...")
            doc_type = classify_document(text)
            logger.info(f"Document geclassificeerd als: {doc_type.value}")
            await ctx.info(f"📋 Gedetecteerd type: {doc_type.value}")
            
            # Extraheer gestructureerde data
            await ctx.info("🤖 Extractie van gestructureerde data...")
            result = await extract_structured_data(text, doc_type, ctx, method_enum)
            
            # Stop timer en record metrics
            processing_time = metrics_collector.stop_timer("document_processing")
            
            if result:
                # Record success metrics
                metrics_collector.record_document_processing(
                    doc_type.value, True, processing_time
                )
                
                await ctx.info(f"✅ Document succesvol verwerkt in {processing_time:.2f}s")
                
                # Convert result to dict for JSON serialization
                if isinstance(result, (CVData, InvoiceData)):
                    result_dict = result.model_dump()
                    result_dict["document_type"] = doc_type.value
                    result_dict["processing_time"] = processing_time
                    return result_dict
                else:
                    return {
                        "document_type": doc_type.value,
                        "processing_time": processing_time,
                        "error": "Onbekend resultaat type"
                    }
            else:
                # Record failure metrics
                metrics_collector.record_document_processing(
                    doc_type.value, False, processing_time, "extraction_failed"
                )
                
                await ctx.error("❌ Document verwerking mislukt")
                return {
                    "document_type": doc_type.value,
                    "processing_time": processing_time,
                    "error": "Extractie mislukt"
                }
            
    except Exception as e:
        # Record failure metrics
        processing_time = metrics_collector.stop_timer("document_processing")
        metrics_collector.record_document_processing(
            "unknown", False, processing_time, f"error: {type(e).__name__}"
        )
        
        # Log de error voor troubleshooting
        logger.error(f"Fout bij document verwerking: {e}", exc_info=True)
        logger.error(f"Input tekst lengte: {len(text)} karakters")
        logger.error(f"Processing time: {processing_time}")
        
        await ctx.error(f"💥 Fout bij document verwerking: {e}")
        return {
            "error": str(e),
            "processing_time": processing_time
        }


@mcp.tool()
async def process_document_file(file_path: str, ctx: Context, extraction_method: str = "json_schema") -> Dict[str, Any]:
    """
    Verwerk een document bestand en extraheer gestructureerde data.
    
    Args:
        file_path: Pad naar het document bestand
        ctx: FastMCP context voor logging en progress
        extraction_method: Extractie methode - "json_schema" (default) of "prompt_parsing"
    
    Returns:
        Dict met geëxtraheerde document data
    """
    try:
        # Onderdruk warnings tijdens bestand verwerking
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            # Converteer string parameter naar enum
            try:
                method_enum = ExtractionMethod(extraction_method.lower())
            except ValueError:
                method_enum = ExtractionMethod.HYBRID
                logger.warning(f"Onbekende extractie methode '{extraction_method}', gebruik HYBRID als default")
            
            # Log input parameters voor troubleshooting
            logger.info(f"process_document_file aangeroepen met bestand: {file_path}, methode: {method_enum.value}")
            
            method_name = "JSON Schema Mode" if method_enum == ExtractionMethod.JSON_SCHEMA else "Prompt Parsing Mode"
            await ctx.info(f"📁 Lezen bestand: {file_path} ({method_name})")
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.error(f"Bestand niet gevonden: {file_path}")
                await ctx.error(f"❌ Bestand niet gevonden: {file_path}")
                return {"error": f"Bestand niet gevonden: {file_path}"}
            
            # Lees tekst uit bestand
            if file_path_obj.suffix.lower() == '.txt':
                with open(file_path_obj, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            elif file_path_obj.suffix.lower() == '.pdf':
                # Voor PDF bestanden gebruik de PDF text extractor
                from mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf
                with open(file_path_obj, 'rb') as f:
                    text_content = extract_text_from_pdf(f.read())
            else:
                logger.error(f"Niet ondersteund bestandstype: {file_path_obj.suffix}")
                await ctx.error(f"❌ Niet ondersteund bestandstype: {file_path_obj.suffix}")
                return {"error": f"Niet ondersteund bestandstype: {file_path_obj.suffix}"}
            
            logger.info(f"Tekst gelezen uit bestand: {len(text_content)} karakters")
            await ctx.info(f"📄 Tekst gelezen: {len(text_content)} karakters")
            
            # Verwerk de tekst
            return await process_document_text(text_content, ctx, method_enum)
        
    except Exception as e:
        logger.error(f"Fout bij bestand verwerking: {e}", exc_info=True)
        await ctx.error(f"💥 Fout bij bestand verwerking: {e}")
        return {"error": str(e)}


@mcp.tool()
async def classify_document_type(text: str, ctx: Context) -> Dict[str, Any]:
    """
    Classificeer alleen het document type zonder volledige verwerking.
    
    Args:
        text: De tekst inhoud van het document
        ctx: FastMCP context voor logging
    
    Returns:
        Dict met document type classificatie
    """
    try:
        # Onderdruk warnings tijdens document classificatie
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            # Log input parameters voor troubleshooting
            logger.info(f"classify_document_type aangeroepen met tekst lengte: {len(text)} karakters")
            logger.debug(f"Tekst preview: {text[:200]}...")
            
            await ctx.info("📊 Classificeren document type...")
            
            doc_type = classify_document(text)
            logger.info(f"Document geclassificeerd als: {doc_type.value}")
            
            await ctx.info(f"📋 Gedetecteerd type: {doc_type.value}")
            
            return {
                "document_type": doc_type.value,
                "confidence": "high" if doc_type != DocumentType.UNKNOWN else "low"
            }
        
    except Exception as e:
        logger.error(f"Fout bij document classificatie: {e}", exc_info=True)
        await ctx.error(f"💥 Fout bij classificatie: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_metrics(ctx: Context) -> Dict[str, Any]:
    """
    Haal huidige metrics op van de document processor.
    
    Args:
        ctx: FastMCP context voor logging
    
    Returns:
        Dict met huidige metrics
    """
    try:
        logger.info("get_metrics aangeroepen")
        await ctx.info("📊 Ophalen metrics...")
        
        metrics = metrics_collector.get_comprehensive_metrics()
        logger.info("Metrics succesvol opgehaald")
        
        await ctx.info("✅ Metrics opgehaald")
        return metrics
        
    except Exception as e:
        logger.error(f"Fout bij ophalen metrics: {e}", exc_info=True)
        await ctx.error(f"💥 Fout bij ophalen metrics: {e}")
        return {"error": str(e)}


@mcp.tool()
async def health_check(ctx: Context) -> Dict[str, Any]:
    """
    Voer een health check uit van de service.
    
    Args:
        ctx: FastMCP context voor logging
    
    Returns:
        Dict met health status
    """
    try:
        logger.info("health_check aangeroepen")
        await ctx.info("🔍 Health check uitvoeren...")
        
        # Test Ollama connectie
        import ollama
        try:
            # Probeer een eenvoudige request naar Ollama
            client = ollama.AsyncClient(host=settings.ollama.HOST)
            models = await client.list()
            ollama_status = "healthy"
            available_models = [model['name'] for model in models.get('models', [])]
            logger.info(f"Ollama status: {ollama_status}, beschikbare modellen: {available_models}")
        except Exception as e:
            ollama_status = f"unhealthy: {e}"
            available_models = []
            logger.error(f"Ollama connectie mislukt: {e}")
        
        # Get basic metrics
        metrics = metrics_collector.get_comprehensive_metrics()
        logger.info("Metrics opgehaald voor health check")
        
        health_data = {
            "status": "healthy" if ollama_status == "healthy" else "degraded",
            "timestamp": metrics["timestamp"],
            "ollama_status": ollama_status,
            "available_models": available_models,
            "uptime": metrics["system"]["uptime"],
            "total_documents_processed": metrics["processing"]["total_documents"],
            "total_ollama_requests": metrics["ollama"]["total_requests"]
        }
        
        logger.info(f"Health check voltooid: {health_data['status']}")
        await ctx.info(f"✅ Health check voltooid: {health_data['status']}")
        return health_data
        
    except Exception as e:
        logger.error(f"Fout bij health check: {e}", exc_info=True)
        await ctx.error(f"💥 Fout bij health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Resource voor het ophalen van voorbeelden
@mcp.resource("examples://document-types")
async def document_types_examples() -> str:
    """Voorbeelden van ondersteunde document types."""
    return """
    # Ondersteunde Document Types
    
    ## CV/Resume
    - Trefwoorden: ervaring, opleiding, vaardigheden, curriculum vitae, werkervaring
    - Geëxtraheerde velden: naam, email, telefoon, werkervaring, opleiding, vaardigheden
    
    ## Factuur/Invoice
    - Trefwoorden: factuur, totaal, bedrag, btw, klant, leverancier
    - Geëxtraheerde velden: factuurnummer, bedragen, datum, bedrijfsinformatie
    
    ## Gebruik
    1. Upload document tekst via process_document_text()
    2. Upload document bestand via process_document_file()
    3. Alleen classificatie via classify_document_type()
    """


# Prompt voor document verwerking instructies
@mcp.prompt("document-processing-guide")
async def document_processing_guide(document_type: str = "any") -> str:
    """Gids voor document verwerking."""
    
    if document_type.lower() == "cv":
        return """
        # CV Verwerking Gids
        
        Voor optimale CV verwerking:
        1. Zorg voor duidelijke secties (Persoonlijke gegevens, Werkervaring, Opleiding)
        2. Gebruik consistente datumformaten
        3. Lijst vaardigheden duidelijk op
        4. Include contactinformatie bovenaan
        
        Voorbeeld gebruik:
        ```
        result = await process_document_text(cv_text)
        print(f"Naam: {result['full_name']}")
        print(f"Email: {result['email']}")
        ```
        """
    elif document_type.lower() == "invoice":
        return """
        # Factuur Verwerking Gids
        
        Voor optimale factuur verwerking:
        1. Zorg voor duidelijk factuurnummer
        2. Include datum en vervaldatum
        3. Lijst alle regels met bedragen
        4. Toon BTW berekening
        5. Include bedrijfsinformatie
        
        Voorbeeld gebruik:
        ```
        result = await process_document_text(invoice_text)
        print(f"Nummer: {result['invoice_number']}")
        print(f"Totaal: €{result['total_amount']}")
        ```
        """
    else:
        return """
        # Document Verwerking Gids
        
        Ondersteunde document types:
        - CV/Resume: Persoonlijke en professionele informatie
        - Factuur/Invoice: Financiële transactie documenten
        
        Algemene stappen:
        1. Document classificatie
        2. Tekst extractie (indien PDF)
        3. Gestructureerde data extractie met AI
        4. Validatie en opschoning
        
        Gebruik process_document_text() voor directe tekst verwerking
        of process_document_file() voor bestanden.
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
