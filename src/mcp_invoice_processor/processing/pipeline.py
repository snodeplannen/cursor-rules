"""
Hoofdpijplijn voor documentverwerking en data-extractie.
"""
import logging
import time
from typing import Union, Type, Any, List
from pydantic import ValidationError
import ollama

from ..config import settings
from ..monitoring.metrics import metrics_collector
from .models import CVData, InvoiceData, ProcessingResult, DocumentType
from .classification import classify_document
from .text_extractor import extract_text_from_pdf
from .chunking import chunk_text, ChunkingMethod
from .merging import merge_partial_cv_data, merge_partial_invoice_data


logger = logging.getLogger(__name__)


async def extract_structured_data(
    text: str,
    doc_type: DocumentType,
    ctx: Any = None
) -> Union[CVData, InvoiceData, None]:
    """
    Extraheert gestructureerde data uit tekst met behulp van Ollama.

    Args:
        text: De tekst om te verwerken
        doc_type: Het gedetecteerde documenttype
        ctx: FastMCP context voor logging (optioneel)

    Returns:
        Union[CVData, InvoiceData, None]: Geëxtraheerde data of None bij fout
    """
    # Start timing voor Ollama request
    start_time = time.time()
    error_type = None
    
    # Log start van extractie
    if ctx:
        try:
            await ctx.info("🤖 Starten AI-gebaseerde data extractie...")
        except Exception:
            pass
    
    # Bepaal het target model en prompt op basis van documenttype
    target_model: Type[Union[CVData, InvoiceData]]
    if doc_type == DocumentType.CV:
        # Specifieke prompt voor CV extractie
        prompt = f"""
        Extract structured information from the following CV text.

        IMPORTANT: Return ONLY valid JSON without any explanation text, comments, or markdown formatting.
        Use EXACTLY these field names in your JSON output:
        - full_name (for the full name)
        - email (for email address)
        - phone_number (for phone number)
        - summary (for summary/objective)
        - work_experience (list of work experiences, each with: job_title, company, start_date, end_date, description)
        - education (list of education, each with: degree, institution, graduation_date)
        - skills (list of skills as strings)
        
        Ensure all required fields are present. If a field cannot be found, use empty string or empty list.
        
        Text:
        {text}
        
        Return ONLY the JSON object, no other text.
        """
        target_model = CVData
    elif doc_type == DocumentType.INVOICE:
        # Specifieke prompt voor factuur extractie
        prompt = f"""
        Extract structured information from the following invoice text.

        IMPORTANT: Return ONLY valid JSON without any explanation text, comments, or markdown formatting.
        Use EXACTLY these field names in your JSON output:
        
        Basic information:
        - invoice_id (for unique identification, use invoice number or generate unique ID)
        - invoice_number (for invoice number)
        - invoice_date (for invoice date)
        - due_date (for due date)
        
        Company information:
        - supplier_name (for supplier name)
        - supplier_address (for supplier address)
        - supplier_vat_number (for supplier VAT number)
        - customer_name (for customer name)
        - customer_address (for customer address)
        - customer_vat_number (for customer VAT number)
        
        Financial information:
        - subtotal (for subtotal excluding VAT)
        - vat_amount (for VAT amount)
        - total_amount (for total including VAT)
        - currency (for currency, default "EUR")
        
        Invoice lines (line_items):
        - description (for product/service description)
        - quantity (for quantity, must be a number, use 1 if not specified)
        - unit_price (for unit price)
        - unit (for unit: pieces, hours, etc.)
        - line_total (for line total)
        - vat_rate (for VAT rate percentage)
        - vat_amount (for VAT amount per line)
        
        Payment information:
        - payment_terms (for payment terms)
        - payment_method (for payment method)
        
        Extra information:
        - notes (for notes)
        - reference (for reference/order number)
        
        CRITICAL: All quantity fields must be numbers (not strings). Use 1 for single items, 0 for discounts/promotions.
        Ensure all required fields are present. If a field cannot be found, use empty string or empty list.
        
        Text:
        {text}
        
        Return ONLY the JSON object, no other text.
        """
        target_model = InvoiceData
    else:
        logger.error(f"Onbekend documenttype: {doc_type}")
        return None

    try:
        # Log Ollama request start
        if ctx:
            try:
                await ctx.info("🤖 Ollama AI model aanroepen...")
            except Exception:
                pass
        
        # Ollama request uitvoeren
        response = ollama.chat(
            model=settings.ollama.MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.1,  # Lage temperature voor consistente output
                "num_predict": 2048,  # Maximum tokens voor response
                "stop": ["```", "```json", "```\n", "\n\n\n"]  # Stop bij code blocks
            }
        )
        
        # Response verwerken
        response_content = response['message']['content'].strip()
        
        # Log response voor debugging
        logger.debug(f"Ollama response: {response_content[:500]}...")
        
        # JSON extractie uit response - verbeterde methode
        json_str = None
        
        # Methode 1: Zoek naar JSON tussen ```json en ``` markers
        if "```json" in response_content:
            start_marker = "```json"
            end_marker = "```"
            start_idx = response_content.find(start_marker) + len(start_marker)
            end_idx = response_content.find(end_marker, start_idx)
            if start_idx != -1 and end_idx != -1:
                json_str = response_content[start_idx:end_idx].strip()
        
        # Methode 2: Zoek naar JSON tussen ``` markers
        elif "```" in response_content:
            parts = response_content.split("```")
            if len(parts) >= 3:
                json_str = parts[1].strip()
        
        # Methode 3: Zoek naar JSON tussen { en }
        if not json_str:
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_content[json_start:json_end]
        
        # Methode 4: Probeer de hele response als JSON
        if not json_str:
            json_str = response_content.strip()
        
        if not json_str:
            logger.error("Geen JSON gevonden in Ollama response")
            logger.error(f"Response content: {response_content}")
            error_type = "json_parsing_error"
            return None
        
        # JSON parsen en valideren
        import json as json_module
        try:
            parsed_data = json_module.loads(json_str)
        except json_module.JSONDecodeError as e:
            logger.error(f"JSON parsing fout: {e}")
            logger.error(f"JSON string: {json_str}")
            logger.error(f"Response content: {response_content}")
            error_type = "json_decode_error"
            return None
        
        # Data valideren met Pydantic model
        try:
            validated_data = target_model(**parsed_data)
        except ValidationError as e:
            logger.error(f"Pydantic validatie fout: {e}")
            logger.error(f"Parsed data: {parsed_data}")
            error_type = "validation_error"
            return None
        
        # Timing stoppen en metrics bijwerken
        processing_time = time.time() - start_time
        metrics_collector.record_ollama_request(
            model=settings.ollama.MODEL,
            response_time=processing_time,
            success=True
        )
        
        # Log succes
        if ctx:
            try:
                await ctx.info(f"✅ Gestructureerde data succesvol geëxtraheerd")
            except Exception:
                pass
        
        logger.info(f"Succesvol gestructureerde data geëxtraheerd uit {doc_type.value} document")
        return validated_data
        
    except Exception as e:
        error_type = "ollama_error"
        logger.error(f"Ollama request fout: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Full error: {str(e)}")
    
    # Timing stoppen en metrics bijwerken bij fout
    processing_time = time.time() - start_time
    metrics_collector.record_ollama_request(
        model=settings.ollama.MODEL,
        response_time=processing_time,
        success=False,
        error_type=error_type
    )
    
    # Log fout
    if ctx:
        try:
            await ctx.error("❌ Data extractie mislukt")
        except Exception:
            pass
    
    return None


async def process_document_pdf(
    pdf_path: str,
    chunking_method: ChunkingMethod = ChunkingMethod.SMART,
    max_chunk_size: int = 4000,
    overlap: int = 200,
    ctx: Any = None
) -> ProcessingResult:
    """
    Verwerkt een PDF document door tekst te extraheren, te chunken en gestructureerde data te extraheren.

    Args:
        pdf_path: Pad naar het PDF bestand
        chunking_method: Methode voor tekst chunking
        max_chunk_size: Maximale grootte per chunk
        overlap: Overlap tussen chunks
        ctx: FastMCP context voor logging

    Returns:
        ProcessingResult: Resultaat van de verwerking
    """
    start_time = time.time()
    
    try:
        # 1. Tekst extraheren uit PDF
        logger.info(f"Tekst extraheren uit PDF: {pdf_path}")
        # Lees het PDF bestand als bytes
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        extracted_text = extract_text_from_pdf(pdf_bytes)
        
        if not extracted_text or len(extracted_text.strip()) < 50:
            return ProcessingResult(
                document_type=DocumentType.UNKNOWN,
                data=None,
                status="failed",
                error_message="Onvoldoende tekst geëxtraheerd uit PDF"
            )
        
        # 2. Documenttype classificeren
        logger.info("Documenttype classificeren")
        doc_type = classify_document(extracted_text)
        logger.info(f"Gedetecteerd documenttype: {doc_type.value}")
        
        # 3. Tekst chunken als deze te lang is
        if len(extracted_text) > max_chunk_size:
            logger.info(f"Tekst chunken (lengte: {len(extracted_text)} karakters)")
            chunks = chunk_text(extracted_text, chunking_method, max_chunk_size, overlap)
            logger.info(f"Tekst opgedeeld in {len(chunks)} chunks")
            
            # 4. Gestructureerde data extraheren uit chunks
            partial_results: List[Union[CVData, InvoiceData]] = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Chunk {i+1}/{len(chunks)} verwerken")
                partial_data = await extract_structured_data(chunk, doc_type, ctx)
                if partial_data:
                    partial_results.append(partial_data)
            
            # 5. Partiële resultaten samenvoegen
            merged_data: Union[CVData, InvoiceData, None] = None
            if partial_results:
                if doc_type == DocumentType.CV:
                    # Filter alleen CV data
                    cv_results = [r for r in partial_results if isinstance(r, CVData)]
                    if cv_results:
                        merged_data = merge_partial_cv_data(cv_results)
                    else:
                        merged_data = None
                elif doc_type == DocumentType.INVOICE:
                    # Filter alleen Invoice data
                    invoice_results = [r for r in partial_results if isinstance(r, InvoiceData)]
                    if invoice_results:
                        merged_data = merge_partial_invoice_data(invoice_results)
                    else:
                        merged_data = None
                else:
                    merged_data = partial_results[0]  # Gebruik eerste resultaat voor onbekende types
                
                if merged_data:
                    processing_time = time.time() - start_time
                    metrics_collector.record_document_processing(
                        doc_type=doc_type.value,
                        success=True,
                        processing_time=processing_time
                    )
                    
                    return ProcessingResult(
                        document_type=doc_type,
                        data=merged_data,
                        status="success",
                        error_message=None
                    )
                else:
                    processing_time = time.time() - start_time
                    metrics_collector.record_document_processing(
                        doc_type=doc_type.value,
                        success=False,
                        processing_time=processing_time,
                        error_type="no_data_extracted"
                    )
                    
                    return ProcessingResult(
                        document_type=doc_type,
                        data=None,
                        status="failed",
                        error_message="Geen gestructureerde data kunnen extraheren uit chunks"
                    )
            else:
                processing_time = time.time() - start_time
                metrics_collector.record_document_processing(
                    doc_type=doc_type.value,
                    success=False,
                    processing_time=processing_time,
                    error_type="no_data_extracted"
                )
                
                return ProcessingResult(
                    document_type=doc_type,
                    data=None,
                    status="failed",
                    error_message="Geen gestructureerde data kunnen extraheren uit chunks"
                )
        else:
            # Tekst is kort genoeg, direct verwerken
            logger.info("Tekst is kort genoeg, direct verwerken")
            extracted_data = await extract_structured_data(extracted_text, doc_type, ctx)
            
            if extracted_data:
                processing_time = time.time() - start_time
                metrics_collector.record_document_processing(
                    doc_type=doc_type.value,
                    success=True,
                    processing_time=processing_time
                )
                
                return ProcessingResult(
                    document_type=doc_type,
                    data=extracted_data,
                    status="success",
                    error_message=None
                )
            else:
                processing_time = time.time() - start_time
                metrics_collector.record_document_processing(
                    doc_type=doc_type.value,
                    success=False,
                    processing_time=processing_time,
                    error_type="extraction_failed"
                )
                
                return ProcessingResult(
                    document_type=doc_type,
                    data=None,
                    status="failed",
                    error_message="Gestructureerde data extractie mislukt"
                )
                
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Onverwachte fout bij verwerken PDF: {str(e)}"
        logger.error(error_msg)
        
        # Bepaal documenttype voor metrics
        doc_type = DocumentType.UNKNOWN
        try:
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            extracted_text = extract_text_from_pdf(pdf_bytes)
            if extracted_text:
                doc_type = classify_document(extracted_text)
        except Exception:
            pass
        
        metrics_collector.record_document_processing(
            doc_type=doc_type.value,
            success=False,
            processing_time=processing_time,
            error_type="unexpected_error"
        )
        
        return ProcessingResult(
            document_type=DocumentType.UNKNOWN,
            data=None,
            status="failed",
            error_message=error_msg
        )


async def process_document_text(
    text: str,
    ctx: Any = None
) -> ProcessingResult:
    """
    Verwerkt documenttekst door deze te classificeren en gestructureerde data te extraheren.

    Args:
        text: De tekst om te verwerken
        ctx: FastMCP context voor logging

    Returns:
        ProcessingResult: Resultaat van de verwerking
    """
    start_time = time.time()
    
    try:
        # 1. Documenttype classificeren
        logger.info("Documenttype classificeren")
        doc_type = classify_document(text)
        logger.info(f"Gedetecteerd documenttype: {doc_type.value}")
        
        # 2. Gestructureerde data extraheren
        logger.info("Gestructureerde data extraheren")
        extracted_data = await extract_structured_data(text, doc_type, ctx)
        
        if extracted_data:
            processing_time = time.time() - start_time
            metrics_collector.record_document_processing(
                doc_type=doc_type.value,
                success=True,
                processing_time=processing_time
            )
            
            return ProcessingResult(
                document_type=doc_type,
                data=extracted_data,
                status="success",
                error_message=None
            )
        else:
            processing_time = time.time() - start_time
            metrics_collector.record_document_processing(
                doc_type=doc_type.value,
                success=False,
                processing_time=processing_time,
                error_type="extraction_failed"
            )
            
            return ProcessingResult(
                document_type=doc_type,
                data=None,
                status="failed",
                error_message="Gestructureerde data extractie mislukt"
            )
            
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Onverwachte fout bij verwerken tekst: {str(e)}"
        logger.error(error_msg)
        
        metrics_collector.record_document_processing(
            doc_type=DocumentType.UNKNOWN.value,
            success=False,
            processing_time=processing_time,
            error_type="unexpected_error"
        )
        
        return ProcessingResult(
            document_type=DocumentType.UNKNOWN,
            data=None,
            status="failed",
            error_message=error_msg
        )


async def process_document_file(
    file_path: str,
    chunking_method: ChunkingMethod = ChunkingMethod.SMART,
    max_chunk_size: int = 4000,
    overlap: int = 200,
    ctx: Any = None
) -> ProcessingResult:
    """
    Verwerkt een document bestand (PDF of tekst) door het juiste pad te kiezen.

    Args:
        file_path: Pad naar het bestand
        chunking_method: Methode voor tekst chunking
        max_chunk_size: Maximale grootte per chunk
        overlap: Overlap tussen chunks
        ctx: FastMCP context voor logging

    Returns:
        ProcessingResult: Resultaat van de verwerking
    """
    if file_path.lower().endswith('.pdf'):
        return await process_document_pdf(file_path, chunking_method, max_chunk_size, overlap, ctx)
    else:
        # Voor tekst bestanden
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return await process_document_text(text, ctx)
        except Exception as e:
            error_msg = f"Fout bij lezen bestand {file_path}: {str(e)}"
            logger.error(error_msg)
            
            return ProcessingResult(
                document_type=DocumentType.UNKNOWN,
                data=None,
                status="failed",
                error_message=error_msg
            )


async def batch_process_documents(
    file_paths: List[str],
    chunking_method: ChunkingMethod = ChunkingMethod.SMART,
    max_chunk_size: int = 4000,
    overlap: int = 200,
    ctx: Any = None
) -> List[ProcessingResult]:
    """
    Verwerkt meerdere documenten in batch.

    Args:
        file_paths: Lijst van bestandspaden
        chunking_method: Methode voor tekst chunking
        max_chunk_size: Maximale grootte per chunk
        overlap: Overlap tussen chunks
        ctx: FastMCP context voor logging

    Returns:
        List[ProcessingResult]: Lijst van verwerkingsresultaten
    """
    results = []
    
    for i, file_path in enumerate(file_paths):
        logger.info(f"Verwerken document {i+1}/{len(file_paths)}: {file_path}")
        
        try:
            result = await process_document_file(
                file_path, chunking_method, max_chunk_size, overlap, ctx
            )
            results.append(result)
            
            if result.status == "success":
                logger.info(f"✅ Document {i+1} succesvol verwerkt")
            else:
                logger.warning(f"⚠️ Document {i+1} verwerking mislukt: {result.error_message}")
                
        except Exception as e:
            logger.error(f"❌ Onverwachte fout bij verwerken document {i+1}: {str(e)}")
            
            # Maak een fout resultaat
            error_result = ProcessingResult(
                document_type=DocumentType.UNKNOWN,
                data=None,
                status="failed",
                error_message=f"Onverwachte fout: {str(e)}"
            )
            results.append(error_result)
    
    # Log samenvatting
    successful = sum(1 for r in results if r.status == "success")
    failed = len(results) - successful
    
    logger.info(f"Batch verwerking voltooid: {successful} succesvol, {failed} mislukt")
    
    return results
