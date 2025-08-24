"""
Type stubs voor mcp_invoice_processor
"""

from .processing.models import (
    DocumentType,
    CVData,
    InvoiceData,
    InvoiceLineItem,
    ProcessingResult,
    WorkExperience,
    Education
)

from .processing.classification import classify_document

__version__: str
__author__: str
__email__: str

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "DocumentType",
    "CVData", 
    "InvoiceData",
    "InvoiceLineItem",
    "ProcessingResult",
    "WorkExperience",
    "Education",
    "classify_document"
]
