"""
Processing utilities module.

Dit module bevat herbruikbare utilities voor document processing:
- Text chunking (chunking.py)
- PDF text extraction (text_extractor.py)
- Legacy model re-exports (models.py) - DEPRECATED

Voor document processing gebruik de nieuwe processors module:
    from processors import InvoiceProcessor, CVProcessor, get_registry
"""

# Herbruikbare utilities
from .chunking import chunk_text, ChunkingMethod
from .text_extractor import extract_text_from_pdf

# Legacy exports voor backward compatibility - DEPRECATED
from .models import (
    DocumentType,
    CVData,
    WorkExperience,
    Education,
    InvoiceData,
    InvoiceLineItem,
)

__all__ = [
    # Utilities
    "chunk_text",
    "ChunkingMethod",
    "extract_text_from_pdf",
    
    # Legacy exports - DEPRECATED
    "DocumentType",
    "CVData",
    "WorkExperience",
    "Education",
    "InvoiceData",
    "InvoiceLineItem",
]
