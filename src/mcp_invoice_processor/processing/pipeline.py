"""
Hoofdpijplijn voor documentverwerking en data-extractie.
"""
import logging
import time
from typing import Union, Type
from pydantic import ValidationError
import ollama

from ..config import settings
from ..monitoring.metrics import metrics_collector
from .models import CVData, InvoiceData, ProcessingResult
from .classification import DocumentType, classify_document
from .text_extractor import extract_text_from_pdf
from .chunking import chunk_text, ChunkingMethod
from .merging import merge_partial_cv_data, merge_partial_invoice_data


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
    # Start timing voor Ollama request
    start_time = time.time()
    error_type = None
    # Bepaal het target model en prompt op basis van documenttype
    target_model: Type[Union[CVData, InvoiceData]]
    if doc_type == DocumentType.CV:
        # Specifieke prompt voor CV extractie
        prompt = f"""
        Extraheer gestructureerde informatie uit de volgende CV-tekst.
        
        BELANGRIJK: Gebruik EXACT deze veldnamen in je JSON output:
        - full_name (voor de volledige naam)
        - email (voor e-mailadres)
        - phone_number (voor telefoonnummer)
        - summary (voor samenvatting/doelstelling)
        - work_experience (lijst van werkervaringen, elk met: job_title, company, start_date, end_date, description)
        - education (lijst van opleidingen, elk met: degree, institution, graduation_date)
        - skills (lijst van vaardigheden als strings)
        
        Zorg ervoor dat alle verplichte velden aanwezig zijn. Als een veld niet gevonden kan worden, gebruik dan een lege string of lege lijst.
        
        Tekst:
        {text}
        
        Output moet een geldig JSON object zijn dat voldoet aan het schema.
        """
        target_model = CVData
    elif doc_type == DocumentType.INVOICE:
        # Specifieke prompt voor factuur extractie
        prompt = f"""
        Extraheer gestructureerde informatie uit de volgende factuur-tekst.
        
        BELANGRIJK: Gebruik EXACT deze veldnamen in je JSON output:
        
        Basis informatie:
        - invoice_id (voor unieke identificatie, gebruik factuurnummer of genereer een unieke ID)
        - invoice_number (voor factuurnummer)
        - invoice_date (voor factuurdatum)
        - due_date (voor vervaldatum)
        
        Bedrijfsinformatie:
        - supplier_name (voor naam leverancier)
        - supplier_address (voor adres leverancier)
        - supplier_vat_number (voor BTW-nummer leverancier)
        - customer_name (voor naam klant)
        - customer_address (voor adres klant)
        - customer_vat_number (voor BTW-nummer klant)
        
        Financiële informatie:
        - subtotal (voor subtotaal exclusief BTW)
        - vat_amount (voor BTW-bedrag)
        - total_amount (voor totaal inclusief BTW)
        - currency (voor valuta, standaard "EUR")
        
        Factuurregels (line_items):
        - description (voor beschrijving product/dienst)
        - quantity (voor aantal)
        - unit_price (voor eenheidsprijs)
        - unit (voor eenheid: stuks, uren, etc.)
        - line_total (voor regeltotaal)
        - vat_rate (voor BTW-tarief percentage)
        - vat_amount (voor BTW-bedrag regel)
        
        Extra informatie:
        - payment_terms (voor betalingsvoorwaarden)
        - payment_method (voor betalingsmethode)
        - notes (voor opmerkingen)
        - reference (voor referentie/ordernummer)
        
        Zorg ervoor dat alle verplichte velden aanwezig zijn. 
        
        KRITIEK VOOR NUMERIEKE VELDEN:
        - quantity, unit_price, line_total, vat_rate, vat_amount, subtotal, total_amount
        - Gebruik ALTIJD 0.0 als standaardwaarde, NOOIT lege strings ('')
        - Als een waarde niet gevonden kan worden, gebruik dan 0.0
        
        VOOR TEKSTVELDEN:
        - Gebruik lege strings ('') als standaardwaarde
        - Als een waarde niet gevonden kan worden, gebruik dan ''
        
        VOOR LIJSTEN:
        - Gebruik lege lijsten ([]) als standaardwaarde
        - Als geen items gevonden kunnen worden, gebruik dan []
        
        Tekst:
        {text}
        
        Output moet een geldig JSON object zijn dat voldoet aan het schema.
        """
        target_model = InvoiceData
    else:
        await ctx.error(f"Onbekend documenttype: {doc_type}")
        return None

    client = ollama.AsyncClient(
        host=settings.ollama.HOST,
        timeout=settings.ollama.TIMEOUT
    )
    schema = target_model.model_json_schema()

    try:
        response = await client.chat(
            model=settings.ollama.MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            format='json',
            options={'json_schema': schema}
        )

        response_content = response['message']['content']
        
        # Log de response voor debugging
        await ctx.info(f"Ollama response ontvangen: {len(response_content)} karakters")
        logger.info(f"Ollama response: {response_content[:200]}...")
        
        # Success tracking for metrics
        result = target_model.model_validate_json(response_content)
        
        # Record metrics voor succesvolle request
        response_time = time.time() - start_time
        metrics_collector.record_ollama_request(
            model=settings.ollama.MODEL,
            response_time=response_time,
            success=True
        )
        
        return result

    except ValidationError as e:
        error_type = "validation_error"
        await ctx.error(f"Pydantic validatiefout: {e}")
        logger.error(f"Validatiefout bij verwerking van {doc_type.value}: {e}")
        
        # Probeer de response te repareren door veldnamen te mappen
        try:
            if doc_type == DocumentType.CV:
                repair_result = await _repair_cv_data(response_content, ctx)
                if repair_result:
                    # Metrics tracking voor gerepareerde data
                    # Record metrics voor gerepareerde request
                    response_time = time.time() - start_time
                    metrics_collector.record_ollama_request(
                        model=settings.ollama.MODEL,
                        response_time=response_time,
                        success=True
                    )
                return repair_result
        except Exception as repair_error:
            await ctx.error(f"Reparatie van CV data mislukt: {repair_error}")
        
        # Record metrics voor mislukte request
        response_time = time.time() - start_time
        metrics_collector.record_ollama_request(
            model=settings.ollama.MODEL,
            response_time=response_time,
            success=False,
            error_type=error_type
        )
        
        return None
    except Exception as e:
        error_type = "communication_error"
        await ctx.error(f"Fout bij communicatie met Ollama: {e}")
        logger.error(f"Ollama communicatiefout: {e}")
        
        # Record metrics voor mislukte request
        response_time = time.time() - start_time
        metrics_collector.record_ollama_request(
            model=settings.ollama.MODEL,
            response_time=response_time,
            success=False,
            error_type=error_type
        )
        
        return None


async def _repair_cv_data(response_content: str, ctx) -> Union[CVData, None]:
    """
    Probeert CV data te repareren door veldnamen te mappen.
    """
    try:
        import json
        
        # Parse de JSON response
        data = json.loads(response_content)
        
        # Map Nederlandse veldnamen naar Engelse veldnamen
        field_mapping = {
            'naam': 'full_name',
            'email': 'email',
            'telefoon': 'phone_number',
            'samenvatting': 'summary',
            'werkervaring': 'work_experience',
            'opleiding': 'education',
            'vaardigheden': 'skills',
            'functie': 'job_title',
            'bedrijf': 'company',
            'startdatum': 'start_date',
            'einddatum': 'end_date',
            'beschrijving': 'description',
            'graad': 'degree',
            'instituut': 'institution',
            'afstudeerdatum': 'graduation_date'
        }
        
        # Repareer de data structuur
        repaired_data = {}
        
        for old_key, new_key in field_mapping.items():
            if old_key in data:
                repaired_data[new_key] = data[old_key]
            elif new_key in data:
                repaired_data[new_key] = data[new_key]
        
        # Zorg ervoor dat alle verplichte velden aanwezig zijn
        if 'full_name' not in repaired_data:
            repaired_data['full_name'] = data.get('naam', 'Onbekend')
        if 'summary' not in repaired_data:
            repaired_data['summary'] = data.get('samenvatting', 'Geen samenvatting beschikbaar')
        if 'work_experience' not in repaired_data:
            repaired_data['work_experience'] = []
        if 'education' not in repaired_data:
            repaired_data['education'] = []
        if 'skills' not in repaired_data:
            repaired_data['skills'] = []
        
        await ctx.info("CV data gerepareerd door veldnamen te mappen")
        logger.info(f"Gerepareerde CV data: {repaired_data}")
        
        return CVData(**repaired_data)
        
    except Exception as e:
        await ctx.error(f"Fout bij repareren van CV data: {e}")
        logger.error(f"CV data reparatie fout: {e}")
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
    # Start timing voor document verwerking
    start_time = time.time()
    
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
            # Record metrics voor mislukte verwerking
            processing_time = time.time() - start_time
            metrics_collector.record_document_processing(
                doc_type="unknown",
                success=False,
                processing_time=processing_time,
                error_type="unknown_document_type"
            )
            
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
                        final_data: Union[CVData, InvoiceData] = merge_partial_cv_data(cv_results)
                    else:
                        # Record metrics voor mislukte verwerking
                        processing_time = time.time() - start_time
                        metrics_collector.record_document_processing(
                            doc_type=doc_type.value,
                            success=False,
                            processing_time=processing_time,
                            error_type="cv_extraction_failed"
                        )
                        
                        return ProcessingResult(
                            document_type=doc_type.value,
                            data=None,
                            status="error",
                            error_message="Kon geen geldige CV data extraheren"
                        )
                elif doc_type == DocumentType.INVOICE:
                    # Type cast voor factuur data
                    invoice_results = [result for result in partial_results if isinstance(result, InvoiceData)]
                    if invoice_results:
                        final_data = merge_partial_invoice_data(invoice_results)
                    else:
                        # Record metrics voor mislukte verwerking
                        processing_time = time.time() - start_time
                        metrics_collector.record_document_processing(
                            doc_type=doc_type.value,
                            success=False,
                            processing_time=processing_time,
                            error_type="invoice_extraction_failed"
                        )
                        
                        return ProcessingResult(
                            document_type=doc_type.value,
                            data=None,
                            status="error",
                            error_message="Kon geen geldige factuur data extraheren"
                        )
                else:
                    # Voor onbekende documenttypes, gebruik het eerste resultaat
                    final_data = partial_results[0]

                await ctx.info("Verwerking voltooid")
                
                # Record metrics voor succesvolle verwerking
                processing_time = time.time() - start_time
                metrics_collector.record_document_processing(
                    doc_type=doc_type.value,
                    success=True,
                    processing_time=processing_time
                )
                
                return ProcessingResult(
                    document_type=doc_type.value,
                    data=final_data,
                    status="success",
                    error_message=None
                )
            else:
                # Record metrics voor mislukte verwerking
                processing_time = time.time() - start_time
                metrics_collector.record_document_processing(
                    doc_type=doc_type.value,
                    success=False,
                    processing_time=processing_time,
                    error_type="chunk_extraction_failed"
                )
                
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
                
                # Record metrics voor succesvolle verwerking
                processing_time = time.time() - start_time
                metrics_collector.record_document_processing(
                    doc_type=doc_type.value,
                    success=True,
                    processing_time=processing_time
                )
                
                return ProcessingResult(
                    document_type=doc_type.value,
                    data=data,
                    status="success",
                    error_message=None
                )
            else:
                # Record metrics voor mislukte verwerking
                processing_time = time.time() - start_time
                metrics_collector.record_document_processing(
                    doc_type=doc_type.value,
                    success=False,
                    processing_time=processing_time,
                    error_type="extraction_failed"
                )
                
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
        
        # Record metrics voor mislukte verwerking
        processing_time = time.time() - start_time
        metrics_collector.record_document_processing(
            doc_type="unknown",
            success=False,
            processing_time=processing_time,
            error_type="unexpected_error"
        )
        
        return ProcessingResult(
            document_type="unknown",
            data=None,
            status="error",
            error_message=str(e)
        )
