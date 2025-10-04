"""
Type stubs voor mcp_invoice_processor.fastmcp_server
"""

from typing import Dict, Any, List, Optional
from fastmcp import FastMCP, Context

# Server instance
mcp: FastMCP

# Server settings
mcp_settings: Any

# Tool functions
async def process_document_text(text: str) -> Dict[str, Any]: ...

async def process_document_file(file_path: str) -> Dict[str, Any]: ...

async def classify_document_type(text: str) -> Dict[str, Any]: ...

async def get_metrics() -> Dict[str, Any]: ...

async def health_check() -> Dict[str, Any]: ...
