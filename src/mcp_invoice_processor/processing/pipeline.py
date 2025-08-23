"""
Hoofdpijplijn voor documentverwerking en data-extractie.
"""
import logging
from typing import Union
from pydantic import ValidationError
import ollama

from ..config import settings
from .models import CVData, InvoiceData, ProcessingResult
from .classification import DocumentType, classify_document
from .text_extractor import extract_text_from_pdf
from .chunking import chunk_text, ChunkingMethod
from .merging import merge_partial_cv_data


logger = logging.getLogger(__name__)


async def extract_structured_data(
    text: str,
    doc_type: DocumentType,
    ctx
) -> Union[CVData, InvoiceData, None]:
    """
    Extraheert gestructureerde data uit tekst met behulp van Ollama.

    Args:
        text: De tekst om te verwerken
        doc_type: Het gedetecteerde documenttype
        ctx: FastMCP context voor logging

    Returns:
        Union[CVData, InvoiceData, None]: Geëxtraheerde data of None bij fout
    """
    if doc_type == DocumentType.CV:
        target_model = CVData
    elif doc_type == DocumentType.INVOICE:
        target_model = InvoiceData
    else:
        await ctx.error(f"Onbekend documenttype: {doc_type}")
        return None

    client = ollama.AsyncClient(
        host=settings.ollama.HOST,
        timeout=settings.ollama.TIMEOUT
    )
    schema = target_model.model_json_schema()

    prompt = f"""
    Extraheer de relevante informatie uit de volgende {doc_type.value.upper()}-tekst.
    Uw output moet een JSON-object zijn dat strikt voldoet aan het opgegeven schema.
    Voeg geen extra commentaar of uitleg toe.

    Tekst:
    {text}
    """

    try:
        response = await client.chat(
            model=settings.ollama.MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            format='json',
            options={'json_schema': schema}
        )

        response_content = response['message']['content']
        return target_model.model_validate_json(response_content)

    except ValidationError as e:
        await ctx.error(f"Pydantic validatiefout: {e}")
        logger.error(f"Validatiefout bij verwerking van {doc_type.value}: {e}")
        return None
    except Exception as e:
        await ctx.error(f"Fout bij communicatie met Ollama: {e}")
        logger.error(f"Ollama communicatiefout: {e}")
        return None


async def process_pdf_document(
    pdf_bytes: bytes,
    file_name: str,
    ctx
) -> ProcessingResult:
    """
    Verwerkt een PDF-document door de volledige pijplijn.

    Args:
        pdf_bytes: De PDF als bytes
        file_name: Naam van het bestand
        ctx: FastMCP context voor logging

    Returns:
        ProcessingResult: Resultaat van de verwerking
    """
    try:
        await ctx.info(f"Start verwerking van {file_name}")

        # Stap 1: Tekstextractie
        await ctx.info("Extraheren van tekst uit PDF...")
        text = extract_text_from_pdf(pdf_bytes)
        await ctx.info(f"Tekst geëxtraheerd: {len(text)} karakters")

        # Stap 2: Documentclassificatie
        await ctx.info("Classificeren van documenttype...")
        doc_type = classify_document(text)
        await ctx.info(f"Document geclassificeerd als: {doc_type.value}")

        if doc_type == DocumentType.UNKNOWN:
            return ProcessingResult(
                document_type="unknown",
                data=None,
                status="error",
                error_message="Kon documenttype niet bepalen"
            )

        # Stap 3: Tekst chunking voor grote documenten
        if len(text) > 2000:  # Drempel voor chunking
            await ctx.info("Document is groot, toepassen van chunking...")
            chunks = chunk_text(text, method=ChunkingMethod.RECURSIVE)
            await ctx.info(f"Document opgedeeld in {len(chunks)} chunks")

            # Verwerk elke chunk
            partial_results = []
            for i, chunk in enumerate(chunks):
                await ctx.info(f"Verwerken van chunk {i+1}/{len(chunks)}...")
                result = await extract_structured_data(chunk, doc_type, ctx)
                if result:
                    partial_results.append(result)

            # Samenvoegen en ontdubbelen van resultaten
            if partial_results:
                await ctx.info("Samenvoegen van partiële resultaten...")
                if doc_type == DocumentType.CV:
                    # Type cast voor CV data
                    cv_results = [result for result in partial_results if isinstance(result, CVData)]
                    if cv_results:
                        final_data = merge_partial_cv_data(cv_results)
                    else:
                        return ProcessingResult(
                            document_type=doc_type.value,
                            data=None,
                            status="error",
                            error_message="Kon geen geldige CV data extraheren"
                        )
                else:
                    # Voor facturen, gebruik het eerste resultaat (kan later uitgebreid worden)
                    final_data = partial_results[0]

                await ctx.info("Verwerking voltooid")
                return ProcessingResult(
                    document_type=doc_type.value,
                    data=final_data,
                    status="success",
                    error_message=None
                )
            else:
                return ProcessingResult(
                    document_type=doc_type.value,
                    data=None,
                    status="error",
                    error_message="Kon geen gestructureerde data extraheren uit chunks"
                )
        else:
            # Voor kleine documenten, direct verwerken
            await ctx.info("Direct verwerken van document...")
            data = await extract_structured_data(text, doc_type, ctx)

            if data:
                await ctx.info("Verwerking voltooid")
                return ProcessingResult(
                    document_type=doc_type.value,
                    data=data,
                    status="success",
                    error_message=None
                )
            else:
                return ProcessingResult(
                    document_type=doc_type.value,
                    data=None,
                    status="error",
                    error_message="Kon geen gestructureerde data extraheren"
                )

    except Exception as e:
        error_msg = f"Onverwachte fout bij verwerking van {file_name}: {e}"
        await ctx.error(error_msg)
        logger.error(error_msg, exc_info=True)
        return ProcessingResult(
            document_type="unknown",
            data=None,
            status="error",
            error_message=str(e)
        )
