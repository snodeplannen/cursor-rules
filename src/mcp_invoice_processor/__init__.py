"""
MCP Invoice Processor - Modulaire document processor met FastMCP.

Nieuwe processor architecture met:
- BaseDocumentProcessor interface
- ProcessorRegistry voor centralized management
- InvoiceProcessor en CVProcessor implementaties
- Volledig async met FastMCP Context integratie
"""

__version__ = "2.0.0"
__author__ = "Uw Naam"
__email__ = "uw.email@example.com"

# Export nieuwe processor architecture
from .processors import (
    BaseDocumentProcessor,
    ProcessorRegistry,
    get_registry,
    register_processor,
    register_processor_resources,
    register_all_processor_resources,
)

from .processors.invoice import (
    InvoiceProcessor,
    InvoiceData,
    InvoiceLineItem,
)

from .processors.cv import (
    CVProcessor,
    CVData,
    WorkExperience,
    Education,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Processor architecture
    "BaseDocumentProcessor",
    "ProcessorRegistry",
    "get_registry",
    "register_processor",
    "register_processor_resources",
    "register_all_processor_resources",
    
    # Invoice processor
    "InvoiceProcessor",
    "InvoiceData",
    "InvoiceLineItem",
    
    # CV processor
    "CVProcessor",
    "CVData",
    "WorkExperience",
    "Education",
]
