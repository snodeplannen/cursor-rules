"""
Processing module voor documentverwerking en data-extractie.
"""

# Export alle belangrijke types en functies
from .models import (
    DocumentType,
    CVData,
    InvoiceData,
    InvoiceLineItem,
    ProcessingResult,
    WorkExperience,
    Education
)

from .classification import classify_document
from .pipeline import extract_structured_data

__all__ = [
    "DocumentType",
    "CVData",
    "InvoiceData", 
    "InvoiceLineItem",
    "ProcessingResult",
    "WorkExperience",
    "Education",
    "classify_document",
    "extract_structured_data"
]
