#!/usr/bin/env python3
"""
FastMCP Server voor document verwerking met Ollama integratie.
Gebaseerd op de Scrapfly MCP guide: https://scrapfly.io/blog/posts/how-to-build-an-mcp-server-in-python-a-complete-guide
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Union, Optional
from fastmcp import FastMCP, Context

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.mcp_invoice_processor.processing.pipeline import extract_structured_data
from src.mcp_invoice_processor.processing.classification import classify_document, DocumentType
from src.mcp_invoice_processor.processing.models import CVData, InvoiceData
from src.mcp_invoice_processor.config import settings
from src.mcp_invoice_processor.monitoring.metrics import metrics_collector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("MCP Invoice Processor")


@mcp.tool()
async def process_document_text(text: str, ctx: Context) -> Dict[str, Any]:
    """
    Verwerk document tekst en extraheer gestructureerde data.
    
    Args:
        text: De tekst inhoud van het document
        ctx: FastMCP context voor logging en progress
    
    Returns:
        Dict met geëxtraheerde document data
    """
    try:
        await ctx.info("🚀 Starten document verwerking...")
        
        # Start metrics timer
        metrics_collector.start_timer("document_processing")
        
        # Classificeer document type
        await ctx.info("📊 Classificeren document type...")
        doc_type = classify_document(text)
        await ctx.info(f"📋 Gedetecteerd type: {doc_type.value}")
        
        # Extraheer gestructureerde data
        await ctx.info("🤖 Extractie van gestructureerde data...")
        result = await extract_structured_data(text, doc_type, ctx)
        
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
        
        await ctx.error(f"💥 Fout bij document verwerking: {e}")
        return {
            "error": str(e),
            "processing_time": processing_time
        }


@mcp.tool()
async def process_document_file(file_path: str, ctx: Context) -> Dict[str, Any]:
    """
    Verwerk een document bestand en extraheer gestructureerde data.
    
    Args:
        file_path: Pad naar het document bestand
        ctx: FastMCP context voor logging en progress
    
    Returns:
        Dict met geëxtraheerde document data
    """
    try:
        await ctx.info(f"📁 Lezen bestand: {file_path}")
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            await ctx.error(f"❌ Bestand niet gevonden: {file_path}")
            return {"error": f"Bestand niet gevonden: {file_path}"}
        
        # Lees tekst uit bestand
        if file_path_obj.suffix.lower() == '.txt':
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                text_content = f.read()
        elif file_path_obj.suffix.lower() == '.pdf':
            # Voor PDF bestanden gebruik de PDF text extractor
            from src.mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf
            with open(file_path_obj, 'rb') as f:
                text_content = extract_text_from_pdf(f.read())
        else:
            await ctx.error(f"❌ Niet ondersteund bestandstype: {file_path_obj.suffix}")
            return {"error": f"Niet ondersteund bestandstype: {file_path_obj.suffix}"}
        
        await ctx.info(f"📄 Tekst gelezen: {len(text_content)} karakters")
        
        # Verwerk de tekst
        return await process_document_text(text_content, ctx)
        
    except Exception as e:
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
        await ctx.info("📊 Classificeren document type...")
        
        doc_type = classify_document(text)
        
        await ctx.info(f"📋 Gedetecteerd type: {doc_type.value}")
        
        return {
            "document_type": doc_type.value,
            "confidence": "high" if doc_type != DocumentType.UNKNOWN else "low"
        }
        
    except Exception as e:
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
        await ctx.info("📊 Ophalen metrics...")
        
        metrics = metrics_collector.get_comprehensive_metrics()
        
        await ctx.info("✅ Metrics opgehaald")
        return metrics
        
    except Exception as e:
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
        await ctx.info("🔍 Health check uitvoeren...")
        
        # Test Ollama connectie
        import ollama
        try:
            # Probeer een eenvoudige request naar Ollama
            client = ollama.AsyncClient(host=settings.ollama.HOST)
            models = await client.list()
            ollama_status = "healthy"
            available_models = [model['name'] for model in models.get('models', [])]
        except Exception as e:
            ollama_status = f"unhealthy: {e}"
            available_models = []
        
        # Get basic metrics
        metrics = metrics_collector.get_comprehensive_metrics()
        
        health_data = {
            "status": "healthy" if ollama_status == "healthy" else "degraded",
            "timestamp": metrics["timestamp"],
            "ollama_status": ollama_status,
            "available_models": available_models,
            "uptime": metrics["system"]["uptime"],
            "total_documents_processed": metrics["processing"]["total_documents"],
            "total_ollama_requests": metrics["ollama"]["total_requests"]
        }
        
        await ctx.info(f"✅ Health check voltooid: {health_data['status']}")
        return health_data
        
    except Exception as e:
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
    logger.info("🚀 Starting MCP Invoice Processor Server...")
    logger.info(f"📊 Ollama host: {settings.ollama.HOST}")
    logger.info(f"🤖 Ollama model: {settings.ollama.MODEL}")
    
    # Run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
