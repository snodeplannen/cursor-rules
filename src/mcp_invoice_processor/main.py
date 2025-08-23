"""
Hoofdapplicatie voor de MCP Invoice Processor.
"""
import base64
from typing import Annotated
from fastmcp import FastMCP, Context

from .config import settings
from .logging_config import setup_logging
from .processing.pipeline import process_pdf_document
from .processing.models import ProcessingResult

# Logging configureren bij het opstarten
setup_logging(log_level=settings.LOG_LEVEL)

mcp = FastMCP(
    name="CV and Invoice Processor",
    instructions="Biedt tools om gestructureerde data te extraheren uit PDF-documenten zoals CV's en facturen."
)


@mcp.tool()
async def process_document(
    file_content_base64: Annotated[str, "Base64-gecodeerde inhoud van het PDF-bestand"],
    file_name: str,
    ctx: Context
) -> ProcessingResult:
    """
    Verwerkt een PDF-document (CV of factuur), extraheert gestructureerde data,
    en retourneert dit als een JSON-object.

    Args:
        file_content_base64: Base64-gecodeerde PDF-inhoud
        file_name: Naam van het bestand
        ctx: FastMCP context voor logging en voortgang

    Returns:
        ProcessingResult: Resultaat van de documentverwerking
    """
    try:
        pdf_bytes = base64.b64decode(file_content_base64)
        result = await process_pdf_document(pdf_bytes, file_name, ctx)
        return result
    except Exception as e:
        await ctx.error(f"Onverwachte fout bij het verwerken van {file_name}: {e}")
        return ProcessingResult(
            document_type="unknown",
            data=None,
            status="error",
            error_message=str(e)
        )


if __name__ == "__main__":
    mcp.run()
