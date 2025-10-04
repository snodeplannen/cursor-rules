"""
Legacy models voor backward compatibility.

DEPRECATED: Gebruik processors.invoice.models en processors.cv.models voor nieuwe code.
"""
from enum import Enum

# Re-export van nieuwe processor models voor backward compatibility
from ..processors.invoice.models import InvoiceData, InvoiceLineItem
from ..processors.cv.models import CVData, WorkExperience, Education


class DocumentType(str, Enum):
    """
    Document type enumeratie.
    
    DEPRECATED: Processors gebruiken nu string-based document_type property.
    Behouden voor backward compatibility met oude code.
    """
    INVOICE = "invoice"
    CV = "cv"
    UNKNOWN = "unknown"


__all__ = [
    "DocumentType",
    "InvoiceData",
    "InvoiceLineItem", 
    "CVData",
    "WorkExperience",
    "Education",
]
