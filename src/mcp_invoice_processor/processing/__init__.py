"""
Processing utilities module.

Herbruikbare utilities voor document processing:
- Text chunking voor grote documenten
- PDF text extraction

Voor document processing gebruik de processors module:
    from mcp_invoice_processor.processors import get_registry, InvoiceProcessor, CVProcessor
"""

from .chunking import chunk_text, ChunkingMethod
from .text_extractor import extract_text_from_pdf

__all__ = [
    # Utilities
    "chunk_text",
    "ChunkingMethod",
    "extract_text_from_pdf",
]
