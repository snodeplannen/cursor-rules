"""
Type stubs voor mcp_invoice_processor.processing.classification
"""

from .models import DocumentType

def classify_document(text: str) -> DocumentType: ...
