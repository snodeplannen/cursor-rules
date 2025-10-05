#!/usr/bin/env python3
"""
Gedeelde MCP tools voor document verwerking.

Deze tools gebruiken de nieuwe modulaire processor architecture met:
- ProcessorRegistry voor centrale processor management
- Async parallel document classificatie  
- FastMCP Context integratie voor logging en progress
- Per-processor statistics tracking
"""

import time
import warnings
from pathlib import Path
from typing import Dict, Any

from .processors import get_registry, register_processor
from .processors.invoice import InvoiceProcessor
from .processors.cv import CVProcessor
from .processing.text_extractor import extract_text_from_pdf
from .config import settings
from .monitoring.metrics import metrics_collector
from .logging_config import setup_logging

# Setup logging
logger = setup_logging(log_level="INFO")

# Initialize and register processors
_processors_initialized = False


def _init_processors():
    """Initialize and register all document processors."""
    global _processors_initialized
    
    if not _processors_initialized:
        register_processor(InvoiceProcessor())
        register_processor(CVProcessor())
        _processors_initialized = True
        logger.info("✅ Document processors geregistreerd: Invoice, CV")


# Initialize processors at module load
_init_processors()


async def process_document_text(text: str, extraction_method: str = "hybrid", model: str | None = None) -> Dict[str, Any]:
    """
    Verwerk document tekst en extraheer gestructureerde data.
    
    Gebruikt de nieuwe processor architecture met:
    - Async parallel classificatie
    - Processor-specifieke extractie
    - Realtime progress reporting
    - Structured logging met metadata
    
    Args:
        text: De tekst inhoud van het document
        extraction_method: Extractie methode - "hybrid" (default), "json_schema" of "prompt_parsing"
        model: Ollama model naam (optioneel, gebruikt settings.ollama.MODEL als niet opgegeven)
    
    Returns:
        Dict met geëxtraheerde document data
    """
    start_time = time.time()
    
    try:
        # Onderdruk warnings tijdens document verwerking
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            # Log input parameters
            logger.info(f"process_document_text: {len(text)} karakters, methode: {extraction_method}, model: {model or 'default'}")
            logger.debug(f"Tekst preview: {text[:200]}...")
            
            # Classificeer document via registry (parallel over alle processors)
            registry = get_registry()
            
            doc_type, confidence, processor = await registry.classify_document(text)
            
            if not processor:
                logger.warning("⚠️ Geen geschikte processor gevonden")
                
                processing_time = time.time() - start_time
                metrics_collector.record_document_processing(
                    "unknown", False, processing_time, "no_processor_found"
                )
                
                return {
                    "error": "Kon document type niet bepalen",
                    "document_type": "unknown",
                    "processing_time": processing_time,
                    "model_used": model or settings.ollama.MODEL
                }
            
            logger.info(f"Document type: {doc_type} ({confidence:.1f}% confidence)")
            
            # Extraheer data via processor
            result = await processor.extract(text, extraction_method, model)
            
            processing_time = time.time() - start_time
            
            if result:
                # Success!
                logger.info(f"✅ Document succesvol verwerkt in {processing_time:.2f}s")
                
                # Update processor statistics
                processor.update_statistics(
                    success=True,
                    processing_time=processing_time,
                    confidence=confidence
                )
                
                # Record global metrics
                metrics_collector.record_document_processing(
                    doc_type, True, processing_time
                )
                
                # Convert to dict
                result_dict = result.model_dump()
                result_dict["document_type"] = doc_type
                result_dict["confidence"] = confidence
                result_dict["processing_time"] = processing_time
                result_dict["processor"] = processor.tool_name
                result_dict["model_used"] = model or settings.ollama.MODEL
                result_dict["success"] = True
                
                return result_dict
            else:
                # Extraction failed
                logger.error("❌ Data extractie mislukt")
                
                processor.update_statistics(
                    success=False,
                    processing_time=processing_time
                )
                
                metrics_collector.record_document_processing(
                    doc_type, False, processing_time, "extraction_failed"
                )
                
                return {
                    "error": "Extractie mislukt",
                    "document_type": doc_type,
                    "processing_time": processing_time,
                    "model_used": model or settings.ollama.MODEL,
                    "success": False
                }
            
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Log error
        logger.error(f"Fout bij document verwerking: {e}", exc_info=True)
        logger.error(f"Input: {len(text)} karakters, tijd: {processing_time:.2f}s")
        
        # Record failure
        metrics_collector.record_document_processing(
            "unknown", False, processing_time, f"error: {type(e).__name__}"
        )
        
        return {
            "error": str(e),
            "processing_time": processing_time,
            "model_used": model or settings.ollama.MODEL,
            "success": False
        }


async def process_document_file(file_path: str, extraction_method: str = "hybrid", model: str | None = None) -> Dict[str, Any]:
    """
    Verwerk een document bestand en extraheer gestructureerde data.
    
    Args:
        file_path: Pad naar het document bestand
        extraction_method: Extractie methode - "hybrid" (default), "json_schema" of "prompt_parsing"
        model: Ollama model naam (optioneel, gebruikt settings.ollama.MODEL als niet opgegeven)
    
    Returns:
        Dict met geëxtraheerde document data
    """
    try:
        # Onderdruk warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            logger.info(f"process_document_file: {file_path}, methode: {extraction_method}")
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.error(f"Bestand niet gevonden: {file_path}")
                return {"error": f"Bestand niet gevonden: {file_path}"}
            
            # Lees tekst uit bestand
            if file_path_obj.suffix.lower() == '.txt':
                with open(file_path_obj, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            elif file_path_obj.suffix.lower() == '.pdf':
                with open(file_path_obj, 'rb') as f:
                    text_content = extract_text_from_pdf(f.read())
            else:
                logger.error(f"Niet ondersteund bestandstype: {file_path_obj.suffix}")
                return {"error": f"Niet ondersteund bestandstype: {file_path_obj.suffix}", "model_used": model or settings.ollama.MODEL, "success": False}
            
            logger.info(f"Tekst gelezen: {len(text_content)} karakters")
            
            # Verwerk de tekst
            return await process_document_text(text_content, extraction_method, model)
        
    except Exception as e:
        logger.error(f"Fout bij bestand verwerking: {e}", exc_info=True)
        return {"error": str(e), "model_used": model or settings.ollama.MODEL, "success": False}


async def classify_document_type(text: str) -> Dict[str, Any]:
    """
    Classificeer alleen het document type zonder volledige verwerking.
    
    Gebruikt async parallel classificatie via alle geregistreerde processors.
    
    Args:
        text: De tekst inhoud van het document
    
    Returns:
        Dict met document type classificatie en confidence scores
    """
    try:
        # Onderdruk warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            logger.info(f"classify_document_type: {len(text)} karakters")
            logger.debug(f"Tekst preview: {text[:200]}...")
            
            # Classificeer via registry (parallel)
            registry = get_registry()
            doc_type, confidence, processor = await registry.classify_document(text)
            
            if processor:
                logger.info(f"Document type: {doc_type} ({confidence:.1f}% confidence)")
                
                return {
                    "document_type": doc_type,
                    "confidence": confidence,
                    "confidence_level": "high" if confidence >= 70 else "medium" if confidence >= 40 else "low",
                    "processor": processor.tool_name,
                    "display_name": processor.display_name
                }
            else:
                logger.warning("⚠️ Kon document type niet bepalen")
                return {
                    "document_type": "unknown",
                    "confidence": 0.0,
                    "confidence_level": "none"
                }
        
    except Exception as e:
        logger.error(f"Fout bij document classificatie: {e}", exc_info=True)
        return {"error": str(e)}


async def get_metrics() -> Dict[str, Any]:
    """
    Haal huidige metrics op van alle processors en het systeem.
    
    Bevat:
    - Global system metrics
    - Per-processor statistics
    - Ollama metrics
    
    Returns:
        Dict met comprehensive metrics
    """
    try:
        logger.info("get_metrics aangeroepen")
        
        # Get global metrics
        global_metrics = metrics_collector.get_comprehensive_metrics()
        
        # Get processor statistics
        registry = get_registry()
        processor_stats = registry.get_all_statistics()
        
        # Combine
        combined_metrics = {
            **global_metrics,
            "processors": processor_stats
        }
        
        logger.info("Metrics succesvol opgehaald")
        
        return combined_metrics
        
    except Exception as e:
        logger.error(f"Fout bij ophalen metrics: {e}", exc_info=True)
        return {"error": str(e)}


async def health_check() -> Dict[str, Any]:
    """
    Voer een health check uit van de service.
    
    Test:
    - Ollama connectie
    - Geregistreerde processors
    - System metrics
    
    Returns:
        Dict met health status
    """
    try:
        logger.info("health_check aangeroepen")
        
        # Test Ollama connectie
        import ollama
        try:
            # Gebruik synchrone client zoals de rest van de code
            models = ollama.list()
            ollama_status = "healthy"
            # Ollama.list() retourneert een object met 'models' attribute
            available_models = [model.model for model in models.models] if hasattr(models, 'models') else []
            logger.info(f"Ollama: {ollama_status}, models: {len(available_models)} available")
        except Exception as e:
            ollama_status = f"unhealthy: {e}"
            available_models = []
            logger.error(f"Ollama connectie mislukt: {e}")
        
        # Check processors
        registry = get_registry()
        processor_types = registry.get_processor_types()
        processor_count = len(processor_types)
        
        # Get metrics
        metrics = metrics_collector.get_comprehensive_metrics()
        processor_stats = registry.get_all_statistics()
        
        health_data = {
            "status": "healthy" if ollama_status == "healthy" else "degraded",
            "timestamp": metrics["timestamp"],
            "ollama": {
                "status": ollama_status,
                "available_models": available_models,
                "model_in_use": settings.ollama.MODEL
            },
            "processors": {
                "count": processor_count,
                "types": processor_types,
                "total_documents_processed": processor_stats["global"]["total_documents_processed"],
                "global_success_rate": processor_stats["global"]["global_success_rate"]
            },
            "system": {
                "uptime": metrics["system"]["uptime"],
                "total_ollama_requests": metrics["ollama"]["total_requests"]
            }
        }
        
        logger.info(f"Health check voltooid: {health_data['status']}")
        
        return health_data
        
    except Exception as e:
        logger.error(f"Fout bij health check: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e)
        }
