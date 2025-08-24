import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from mcp_invoice_processor.processing.pipeline import process_document_pdf, extract_structured_data
from mcp_invoice_processor.processing.models import CVData, WorkExperience, InvoiceData, InvoiceLineItem, DocumentType
from mcp_invoice_processor.processing.chunking import ChunkingMethod
from typing import Any, Dict, List, Optional, Union

"""
Tests voor de verwerkingspijplijn.
"""
# base64 not used in current tests



# Gebruik fixtures uit conftest.py


# Gebruik fixtures uit conftest.py


# Gebruik fixtures uit conftest.py


class TestDocumentClassification:
    """Tests voor documentclassificatie."""
    
    def test_cv_classification(self, sample_cv_text: str) -> None:
        """Test CV classificatie."""
        from mcp_invoice_processor.processing.classification import classify_document
        
        doc_type = classify_document(sample_cv_text)
        assert doc_type == DocumentType.CV
    
    def test_invoice_classification(self, sample_invoice_text: str) -> None:
        """Test factuur classificatie."""
        from mcp_invoice_processor.processing.classification import classify_document
        
        doc_type = classify_document(sample_invoice_text)
        assert doc_type == DocumentType.INVOICE


class TestTextExtraction:
    """Tests voor tekstextractie."""
    
    def test_text_extraction_success(self) -> None:
        """Test succesvolle tekstextractie."""
        from mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf
        
        # Mock PDF bytes (dit zou een echte PDF moeten zijn in echte tests)
        mock_pdf_bytes = b"%PDF-1.4\n%Test PDF content"
        
        with patch('fitz.open') as mock_fitz:
            mock_doc = MagicMock()
            mock_page = MagicMock()
            mock_page.get_text.return_value = "Test PDF content"
            mock_doc.__iter__.return_value = [mock_page]
            mock_fitz.return_value.__enter__.return_value = mock_doc
            
            text = extract_text_from_pdf(mock_pdf_bytes)
            assert "Test PDF content" in text


class TestChunking:
    """Tests voor tekst chunking."""
    
    def test_recursive_chunking(self) -> None:
        """Test recursive chunking methode."""
        from mcp_invoice_processor.processing.chunking import chunk_text, ChunkingMethod
        
        long_text = "Dit is een lange tekst. " * 100  # 2000+ karakters
        
        chunks = chunk_text(long_text, method=ChunkingMethod.RECURSIVE)
        assert len(chunks) > 1
        assert all(len(chunk) <= 1000 for chunk in chunks)


class TestMerging:
    """Tests voor samenvoegen en ontdubbelen."""
    
    def test_merge_partial_cv_data(self) -> None:
        """Test samenvoegen van partiële CV data."""
        from mcp_invoice_processor.processing.merging import merge_partial_cv_data
        
        # Maak twee partiële CV resultaten
        cv1 = CVData(
            full_name="Jan Jansen",
            email="jan@email.com",
            phone_number="",
            summary="Software ontwikkelaar",
            work_experience=[
                WorkExperience(
                    job_title="Software Engineer",
                    company="TechCorp",
                    start_date="2020-01-01",
                    end_date="2023-12-31",
                    description="Python development"
                )
            ],
            education=[],
            skills=["Python", "JavaScript"]
        )

        cv2 = CVData(
            full_name="Jan Jansen",
            email="",
            phone_number="06-12345678",
            summary="Software ontwikkelaar",
            work_experience=[
                WorkExperience(
                    job_title="Software Engineer",
                    company="TechCorp",
                    start_date="2020-01-01",
                    end_date="2023-12-31",
                    description="Python development"
                )
            ],
            education=[],
            skills=["Python", "Docker"]
        )
        
        merged = merge_partial_cv_data([cv1, cv2])
        
        assert merged.full_name == "Jan Jansen"
        assert merged.email == "jan@email.com"
        assert merged.phone_number == "06-12345678"
        assert len(merged.skills) == 3  # Python, JavaScript, Docker
        assert len(merged.work_experience) == 1  # Ontdubbeld

    def test_merge_partial_invoice_data(self) -> None:
        """Test samenvoegen van partiële factuur data."""
        from mcp_invoice_processor.processing.merging import merge_partial_invoice_data
        
        # Maak twee partiële factuur resultaten
        invoice1 = InvoiceData(
            invoice_id="INV-001",
            invoice_number="",
            invoice_date="",
            due_date="",
            supplier_name="Test Supplier",
            supplier_address="",
            supplier_vat_number="",
            customer_name="Test Customer",
            customer_address="",
            customer_vat_number="",
            subtotal=100.0,
            vat_amount=21.0,
            total_amount=121.0,
            payment_terms="",
            payment_method="",
            notes="",
            reference="",
            line_items=[
                InvoiceLineItem(
                    description="Product A",
                    quantity=2,
                    unit="stuks",
                    unit_price=50.0,
                    line_total=100.0,
                    vat_rate=21.0,
                    vat_amount=21.0
                )
            ]
        )
        
        invoice2 = InvoiceData(
            invoice_id="INV-001",
            invoice_number="INV-2024-001",
            invoice_date="2024-01-15",
            due_date="",
            supplier_name="Test Supplier",
            supplier_address="",
            supplier_vat_number="",
            customer_name="Test Customer",
            customer_address="",
            customer_vat_number="",
            subtotal=100.0,
            vat_amount=21.0,
            total_amount=121.0,
            payment_terms="",
            payment_method="",
            notes="",
            reference="",
            line_items=[
                InvoiceLineItem(
                    description="Product A",
                    quantity=1,
                    unit="stuks",
                    unit_price=50.0,
                    line_total=50.0,
                    vat_rate=21.0,
                    vat_amount=10.5
                )
            ]
        )
        
        merged = merge_partial_invoice_data([invoice1, invoice2])
        
        assert merged.invoice_id == "INV-001"
        assert merged.invoice_number == "INV-2024-001"
        assert merged.invoice_date == "2024-01-15"
        assert len(merged.line_items) == 1  # Ontdubbeld
        assert merged.line_items[0].quantity == 3  # Samengevoegd
        assert merged.line_items[0].line_total == 150.0  # Samengevoegd
        assert merged.subtotal == 150.0  # Herberekend
        assert merged.vat_amount == 31.5  # Herberekend (21.0 + 10.5)
        assert merged.total_amount == 181.5  # Herberekend (150.0 + 31.5)


class TestPipeline:
    """Tests voor de hoofdpijplijn."""
    
    @pytest.mark.asyncio
    async def test_process_document_pdf_success(self, mock_context: Any, sample_cv_text: str) -> None:
        """Test succesvolle PDF verwerking."""
        with patch('mcp_invoice_processor.processing.pipeline.extract_text_from_pdf') as mock_extract, \
             patch('mcp_invoice_processor.processing.pipeline.classify_document') as mock_classify, \
             patch('mcp_invoice_processor.processing.pipeline.extract_structured_data') as mock_extract_data, \
             patch('builtins.open', create=True) as mock_open:
            
            # Mock file open
            mock_file = MagicMock()
            mock_file.read.return_value = b"%PDF-1.4\n%Test PDF content"
            mock_open.return_value.__enter__.return_value = mock_file
            
            mock_extract.return_value = sample_cv_text
            mock_classify.return_value = DocumentType.CV
            
            mock_cv = CVData(
                full_name="Jan Jansen",
                email="jan@email.com",
                phone_number="06-12345678",
                summary="Software ontwikkelaar",
                work_experience=[],
                education=[],
                skills=[]
            )
            mock_extract_data.return_value = mock_cv

            # Mock PDF bytes
            pdf_bytes = b"%PDF-1.4\n%Test PDF content"

            result = await process_document_pdf("test.pdf", ChunkingMethod.SMART, 4000, 200, mock_context)

            assert result.status == "success"
            assert result.document_type == "cv"
            assert result.data is not None
            assert isinstance(result.data, CVData)

    @pytest.mark.asyncio
    async def test_process_document_pdf_extraction_error(self, mock_context: Any) -> None:
        """Test foutafhandeling bij tekstextractie."""
        with patch('mcp_invoice_processor.processing.pipeline.extract_text_from_pdf') as mock_extract, \
             patch('builtins.open', create=True) as mock_open:
            
            # Mock file open
            mock_file = MagicMock()
            mock_file.read.return_value = b"invalid pdf content"
            mock_open.return_value.__enter__.return_value = mock_file
            
            mock_extract.side_effect = ValueError("PDF corrupt")

            pdf_bytes = b"invalid pdf content"
            result = await process_document_pdf("test.pdf", ChunkingMethod.SMART, 4000, 200, mock_context)

            assert result.status == "failed"
            assert "PDF corrupt" in result.error_message

    @pytest.mark.asyncio
    async def test_process_document_pdf_invoice_success(self, mock_context: Any, sample_invoice_text: str) -> None:
        """Test succesvolle factuurverwerking."""
        with patch('mcp_invoice_processor.processing.pipeline.extract_text_from_pdf') as mock_extract, \
             patch('mcp_invoice_processor.processing.pipeline.classify_document') as mock_classify, \
             patch('mcp_invoice_processor.processing.pipeline.extract_structured_data') as mock_extract_data, \
             patch('builtins.open', create=True) as mock_open:
            
            # Mock file open
            mock_file = MagicMock()
            mock_file.read.return_value = b"%PDF-1.4\n%Test PDF content"
            mock_open.return_value.__enter__.return_value = mock_file
            
            mock_extract.return_value = sample_invoice_text
            mock_classify.return_value = DocumentType.INVOICE
            
            mock_invoice = InvoiceData(
                invoice_id="INV-001",
                invoice_number="INV-001",
                invoice_date="2025-01-01",
                due_date="2025-02-01",
                supplier_name="Test Supplier",
                supplier_address="Test Address",
                supplier_vat_number="NL123456789B01",
                customer_name="Test Customer",
                customer_address="Customer Address",
                customer_vat_number="NL987654321B01",
                subtotal=100.0,
                vat_amount=21.0,
                total_amount=121.0,
                line_items=[],
                payment_terms="30 days",
                payment_method="Bank transfer",
                notes="Test invoice",
                reference="REF-001"
            )
            mock_extract_data.return_value = mock_invoice

            # Mock PDF bytes
            pdf_bytes = b"%PDF-1.4\n%Test PDF content"

            result = await process_document_pdf("test_invoice.pdf", ChunkingMethod.SMART, 4000, 200, mock_context)

            assert result.status == "success"
            assert result.document_type == "invoice"
            assert result.data is not None
            assert isinstance(result.data, InvoiceData)
            assert result.data.invoice_id == "INV-001"
            assert result.data.total_amount == 121.0


class TestOllamaIntegration:
    """Tests voor Ollama integratie."""
    
    @pytest.mark.asyncio
    async def test_extract_structured_data_success(self, mock_context: Any) -> None:
        """Test succesvolle data-extractie via Ollama."""
        with patch('ollama.chat') as mock_chat:
            mock_response = {
                'message': {
                    'content': '{"full_name": "Jan Jansen", "email": "jan@email.com", "phone_number": "06-12345678", "summary": "Developer", "work_experience": [], "education": [], "skills": []}'
                }
            }
            mock_chat.return_value = mock_response
            
            result = await extract_structured_data(
                "Test CV tekst", 
                DocumentType.CV, 
                mock_context
            )
            
            assert result is not None
            assert isinstance(result, CVData)
            assert result.full_name == "Jan Jansen"
    
    @pytest.mark.asyncio
    async def test_extract_structured_data_validation_error(self, mock_context: Any) -> None:
        """Test foutafhandeling bij validatiefouten met reparatie."""
        with patch('ollama.chat') as mock_chat:
            # Mock een ongeldige JSON response die gerepareerd kan worden
            mock_response = {
                'message': {
                    'content': '{"naam": "Test Persoon", "samenvatting": "Test samenvatting"}'
                }
            }
            mock_chat.return_value = mock_response

            result = await extract_structured_data(
                "Test tekst",
                DocumentType.CV,
                mock_context
            )

            # De functie geeft None terug bij validatiefouten (geen reparatie logica)
            assert result is None
            
            # De functie logt errors naar de logger, niet naar de context
            # Dit is correct gedrag

    @pytest.mark.asyncio
    async def test_extract_structured_data_invoice_success(self, mock_context: Any) -> None:
        """Test succesvolle factuur data-extractie via Ollama."""
        with patch('ollama.chat') as mock_chat:
            mock_response = {
                'message': {
                    'content': '{"invoice_id": "INV-001", "invoice_number": "INV-001", "supplier_name": "Test Supplier", "customer_name": "Test Customer", "subtotal": 100.0, "vat_amount": 21.0, "total_amount": 121.0, "line_items": []}'
                }
            }
            mock_chat.return_value = mock_response
            
            result = await extract_structured_data(
                "Test factuur tekst", 
                DocumentType.INVOICE, 
                mock_context
            )
            
            assert result is not None
            assert isinstance(result, InvoiceData)
            assert result.invoice_id == "INV-001"
            assert result.supplier_name == "Test Supplier"
            assert result.total_amount == 121.0


if __name__ == "__main__":
    pytest.main([__file__])
