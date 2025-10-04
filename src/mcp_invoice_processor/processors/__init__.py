"""
Document Processors Module.

Modulaire, uitbreidbare architectuur voor document type processing.
Elk processor type is volledig zelfstandig met eigen classificatie, extractie,
validatie en metrics.

Usage:
    >>> from processors import get_registry, register_processor
    >>> from processors.invoice import InvoiceProcessor
    >>> 
    >>> # Registreer processor
    >>> register_processor(InvoiceProcessor())
    >>> 
    >>> # Gebruik registry voor classificatie
    >>> registry = get_registry()
    >>> doc_type, confidence, processor = await registry.classify_document(text, ctx)
    >>> 
    >>> # Extraheer data
    >>> if processor:
    ...     data = await processor.extract(text, ctx, method="hybrid")

References:
    - https://gofastmcp.com/servers/context
    - https://gofastmcp.com/servers/resources
    - https://gofastmcp.com/servers/tools
"""

from .base import (
    BaseDocumentProcessor,
    ProcessingStage,
    ProcessingStatus,
)

from .registry import (
    ProcessorRegistry,
    get_registry,
    register_processor,
    register_processor_resources,
    register_all_processor_resources,
)

__all__ = [
    # Base classes
    "BaseDocumentProcessor",
    "ProcessingStage",
    "ProcessingStatus",
    
    # Registry
    "ProcessorRegistry",
    "get_registry",
    "register_processor",
    
    # MCP Resource registration
    "register_processor_resources",
    "register_all_processor_resources",
]

__version__ = "2.0.0"

