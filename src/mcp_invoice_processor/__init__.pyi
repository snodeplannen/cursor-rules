"""
Type stubs voor mcp_invoice_processor.

Nieuwe processor architecture.
"""

from .processors import (
    BaseDocumentProcessor as BaseDocumentProcessor,
    ProcessorRegistry as ProcessorRegistry,
    get_registry as get_registry,
    register_processor as register_processor,
    register_processor_resources as register_processor_resources,
    register_all_processor_resources as register_all_processor_resources,
)

from .processors.invoice import (
    InvoiceProcessor as InvoiceProcessor,
    InvoiceData as InvoiceData,
    InvoiceLineItem as InvoiceLineItem,
)

from .processors.cv import (
    CVProcessor as CVProcessor,
    CVData as CVData,
    WorkExperience as WorkExperience,
    Education as Education,
)

__version__: str
__author__: str
__email__: str

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "BaseDocumentProcessor",
    "ProcessorRegistry",
    "get_registry",
    "register_processor",
    "register_processor_resources",
    "register_all_processor_resources",
    "InvoiceProcessor",
    "InvoiceData",
    "InvoiceLineItem",
    "CVProcessor",
    "CVData",
    "WorkExperience",
    "Education",
]
