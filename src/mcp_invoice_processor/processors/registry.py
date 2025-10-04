"""
Processor Registry voor document type management.

Beheert alle geregistreerde document processors en voorziet in:
- Processor registratie en lookup
- Async document classificatie met confidence scoring
- Aggregated statistics van alle processors
- MCP tool en resource metadata generatie
"""

import asyncio
import logging
from typing import Dict, Optional, List, Tuple, Any

from fastmcp import Context, FastMCP, Annotations

from .base import BaseDocumentProcessor

logger = logging.getLogger(__name__)


class ProcessorRegistry:
    """
    Registry voor document processors met async support.
    
    Beheert alle geregistreerde processors en voorziet in:
    - Processor registratie en lookup
    - Async document classificatie met confidence scoring
    - Aggregated statistics van alle processors
    - MCP tool metadata generatie
    """
    
    def __init__(self):
        """Initialiseer registry."""
        self._processors: Dict[str, BaseDocumentProcessor] = {}
    
    def register(self, processor: BaseDocumentProcessor) -> None:
        """
        Registreer een nieuwe processor.
        
        Args:
            processor: Document processor om te registreren
            
        Raises:
            ValueError: Als een processor met dit type al geregistreerd is
        """
        doc_type = processor.document_type
        
        if doc_type in self._processors:
            raise ValueError(
                f"Processor voor type '{doc_type}' is al geregistreerd. "
                f"Gebruik unregister() eerst om te vervangen."
            )
        
        self._processors[doc_type] = processor
        logger.info(
            f"✅ Processor geregistreerd: {processor.display_name} ({doc_type})",
            extra={
                "processor_type": doc_type,
                "tool_name": processor.tool_name
            }
        )
    
    def unregister(self, doc_type: str) -> bool:
        """
        Verwijder een processor.
        
        Args:
            doc_type: Document type om te verwijderen
            
        Returns:
            bool: True als verwijderd, False als niet gevonden
        """
        if doc_type in self._processors:
            processor = self._processors.pop(doc_type)
            logger.info(f"❌ Processor verwijderd: {processor.display_name}")
            return True
        return False
    
    def get_processor(self, doc_type: str) -> Optional[BaseDocumentProcessor]:
        """
        Haal processor op voor documenttype.
        
        Args:
            doc_type: Document type identifier
            
        Returns:
            Optional[BaseDocumentProcessor]: Processor of None als niet gevonden
        """
        return self._processors.get(doc_type)
    
    async def classify_document(
        self, 
        text: str,
        ctx: Optional[Context] = None
    ) -> Tuple[str, float, Optional[BaseDocumentProcessor]]:
        """
        Classificeer document door alle processors async te proberen.
        
        Alle processors worden parallel uitgevoerd voor snelheid.
        De processor met de hoogste confidence score wint.
        
        Args:
            text: Document tekst om te classificeren
            ctx: FastMCP context voor logging
            
        Returns:
            Tuple[str, float, Optional[BaseDocumentProcessor]]: 
                (documenttype, confidence_score, processor)
                
        Example:
            >>> registry = ProcessorRegistry()
            >>> doc_type, confidence, processor = await registry.classify_document(text, ctx)
            >>> print(f"Type: {doc_type}, Confidence: {confidence}%")
        """
        if not self._processors:
            logger.warning("Geen processors geregistreerd in registry")
            return "unknown", 0.0, None
        
        if ctx:
            await ctx.debug(
                f"Classificeren document met {len(self._processors)} processors...",
                extra={"processor_count": len(self._processors)}
            )
        
        # Voer alle classificaties parallel uit voor snelheid
        tasks = [
            processor.classify(text, ctx) 
            for processor in self._processors.values()
        ]
        
        try:
            scores = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Fout bij parallel classificeren: {e}")
            if ctx:
                await ctx.error(f"Classificatie fout: {e}")
            return "unknown", 0.0, None
        
        # Zoek beste score
        best_score = 0.0
        best_processor = None
        
        for processor, score in zip(self._processors.values(), scores):
            # Skip processors die een exception gaven
            if isinstance(score, Exception):
                logger.error(
                    f"Processor {processor.document_type} gaf fout: {score}",
                    extra={"processor": processor.document_type}
                )
                continue
            
            if ctx:
                await ctx.debug(
                    f"{processor.display_name}: {score:.1f}% confidence",
                    extra={
                        "processor": processor.document_type,
                        "confidence": score
                    }
                )
            
            if score > best_score:
                best_score = score
                best_processor = processor
        
        if best_processor:
            if ctx:
                await ctx.info(
                    f"📋 Beste match: {best_processor.display_name} ({best_score:.1f}% confidence)",
                    extra={
                        "document_type": best_processor.document_type,
                        "confidence": best_score
                    }
                )
            return best_processor.document_type, best_score, best_processor
        
        if ctx:
            await ctx.warning("Geen processor kon documenttype bepalen")
        
        return "unknown", 0.0, None
    
    def get_all_processors(self) -> List[BaseDocumentProcessor]:
        """
        Haal alle geregistreerde processors op.
        
        Returns:
            List[BaseDocumentProcessor]: Lijst van alle processors
        """
        return list(self._processors.values())
    
    def get_processor_types(self) -> List[str]:
        """
        Haal alle geregistreerde documenttypes op.
        
        Returns:
            List[str]: Lijst van document type identifiers
        """
        return list(self._processors.keys())
    
    def get_all_statistics(self) -> Dict[str, Any]:
        """
        Haal gecombineerde statistics van alle processors op.
        
        Returns:
            Dict: Aggregated statistics van alle processors
        """
        all_stats = {
            "total_processors": len(self._processors),
            "processor_types": self.get_processor_types(),
            "processors": {}
        }
        
        # Verzamel stats per processor
        total_processed = 0
        total_successful = 0
        total_failed = 0
        
        for doc_type, processor in self._processors.items():
            processor_stats = processor.get_statistics()
            all_stats["processors"][doc_type] = processor_stats
            
            total_processed += processor_stats["total_processed"]
            total_successful += processor_stats["total_successful"]
            total_failed += processor_stats["total_failed"]
        
        # Bereken globale statistieken
        all_stats["global"] = {
            "total_documents_processed": total_processed,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "global_success_rate": (
                (total_successful / total_processed * 100) 
                if total_processed > 0 else 0.0
            )
        }
        
        return all_stats
    
    def get_tool_metadata_list(self) -> List[Dict[str, Any]]:
        """
        Genereer MCP tool metadata voor alle processors.
        
        Gebruikt voor automatische MCP tool registratie.
        
        Returns:
            List[Dict]: Lijst van tool metadata voor elke processor
        """
        return [
            processor.tool_metadata 
            for processor in self._processors.values()
        ]


# Global singleton registry instance
_global_registry: Optional[ProcessorRegistry] = None


def get_registry() -> ProcessorRegistry:
    """
    Haal de globale processor registry op (singleton pattern).
    
    Returns:
        ProcessorRegistry: De globale registry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ProcessorRegistry()
    return _global_registry


def register_processor(processor: BaseDocumentProcessor) -> None:
    """
    Convenience functie om processor bij globale registry te registreren.
    
    Args:
        processor: Processor om te registreren
    """
    registry = get_registry()
    registry.register(processor)


# ==================== MCP RESOURCE REGISTRATION ====================

def register_processor_resources(mcp: FastMCP, processor: BaseDocumentProcessor) -> None:
    """
    Registreer alle MCP resources voor een processor.
    
    Dit maakt processor data beschikbaar via MCP Resources protocol:
    - stats://{doc_type} - Processor statistics
    - schema://{doc_type} - JSON schema van data model
    - keywords://{doc_type} - Classificatie keywords
    
    Args:
        mcp: FastMCP server instance
        processor: Processor om resources voor te registreren
        
    References:
        - https://gofastmcp.com/servers/resources
    
    Example:
        >>> mcp = FastMCP("DocumentProcessor")
        >>> invoice_processor = InvoiceProcessor()
        >>> register_processor_resources(mcp, invoice_processor)
    """
    doc_type = processor.document_type
    display_name = processor.display_name
    
    # Resource 1: Statistics
    @mcp.resource(
        uri=f"stats://{doc_type}",
        name=f"{display_name} Statistics",
        description=f"Processor statistics voor {display_name} documenten",
        mime_type="application/json",
        annotations=Annotations(
            readOnlyHint=True,
            idempotentHint=True
        ),
        meta={
            "processor_type": doc_type,
            "resource_type": "statistics"
        }
    )
    async def get_stats(ctx: Context) -> Dict[str, Any]:
        return await processor.get_statistics_resource(ctx)
    
    # Resource 2: JSON Schema
    @mcp.resource(
        uri=f"schema://{doc_type}",
        name=f"{display_name} Schema",
        description=f"JSON schema voor {display_name} data extractie",
        mime_type="application/json",
        annotations=Annotations(
            readOnlyHint=True,
            idempotentHint=True
        ),
        meta={
            "processor_type": doc_type,
            "resource_type": "schema"
        }
    )
    async def get_schema(ctx: Context) -> Dict[str, Any]:
        return await processor.get_schema_resource(ctx)
    
    # Resource 3: Keywords
    @mcp.resource(
        uri=f"keywords://{doc_type}",
        name=f"{display_name} Keywords",
        description=f"Classificatie keywords voor {display_name} detectie",
        mime_type="application/json",
        annotations=Annotations(
            readOnlyHint=True,
            idempotentHint=True
        ),
        meta={
            "processor_type": doc_type,
            "resource_type": "keywords"
        }
    )
    async def get_keywords(ctx: Context) -> Dict[str, Any]:
        return await processor.get_keywords_resource(ctx)
    
    logger.info(
        f"✅ MCP Resources geregistreerd voor {display_name}",
        extra={
            "processor_type": doc_type,
            "resources": ["stats", "schema", "keywords"]
        }
    )


def register_all_processor_resources(mcp: FastMCP) -> None:
    """
    Registreer MCP resources voor alle processors in de registry.
    
    Args:
        mcp: FastMCP server instance
        
    Example:
        >>> mcp = FastMCP("DocumentProcessor")
        >>> register_processor(InvoiceProcessor())
        >>> register_processor(CVProcessor())
        >>> register_all_processor_resources(mcp)
    """
    registry = get_registry()
    
    for processor in registry.get_all_processors():
        register_processor_resources(mcp, processor)
    
    # Registreer ook een global statistics resource
    @mcp.resource(
        uri="stats://all",
        name="All Processors Statistics",
        description="Gecombineerde statistics van alle document processors",
        mime_type="application/json",
        annotations=Annotations(
            readOnlyHint=True,
            idempotentHint=True
        ),
        meta={
            "resource_type": "global_statistics"
        }
    )
    async def get_all_stats(ctx: Context) -> Dict[str, Any]:
        await ctx.debug("Ophalen global statistics")
        return registry.get_all_statistics()
    
    logger.info("✅ Global statistics resource geregistreerd: stats://all")

