"""
Tests voor de verwerkingspijplijn.

UPDATED: Nu met nieuwe processor architecture.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Nieuwe processor imports
from mcp_invoice_processor.processors import get_registry, ProcessorRegistry
from mcp_invoice_processor.processors.invoice import InvoiceProcessor, InvoiceData, InvoiceLineItem
from mcp_invoice_processor.processors.cv import CVProcessor, CVData, WorkExperience, Education

# Utilities
from mcp_invoice_processor.processing.chunking import chunk_text, ChunkingMethod
from mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf


class TestDocumentClassification:
    """Tests voor documentclassificatie met nieuwe processors."""
    
    @pytest.mark.asyncio
    async def test_cv_classification(self, sample_cv_text: str) -> None:
        """Test CV classificatie via processor."""
        processor = CVProcessor()
        confidence = await processor.classify(sample_cv_text)
        
        # CV tekst moet hoge confidence geven
        assert confidence > 30, f"Expected CV confidence > 30, got {confidence}"
    
    @pytest.mark.asyncio
    async def test_invoice_classification(self, sample_invoice_text: str) -> None:
        """Test factuur classificatie via processor."""
        processor = InvoiceProcessor()
        confidence = await processor.classify(sample_invoice_text)
        
        # Invoice tekst moet hoge confidence geven  
        assert confidence > 30, f"Expected invoice confidence > 30, got {confidence}"
    
    @pytest.mark.asyncio
    async def test_registry_classification(self, sample_invoice_text: str) -> None:
        """Test classificatie via registry (parallel)."""
        registry = ProcessorRegistry()
        registry.register(InvoiceProcessor())
        registry.register(CVProcessor())
        
        doc_type, confidence, processor = await registry.classify_document(sample_invoice_text)
        
        assert doc_type == "invoice"
        assert processor is not None
        assert confidence > 0


class TestTextExtraction:
    """Tests voor tekstextractie."""
    
    def test_text_extraction_success(self) -> None:
        """Test succesvolle tekstextractie."""
        # Mock PDF bytes
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
        long_text = "Dit is een lange tekst. " * 100  # 2000+ karakters
        
        chunks = chunk_text(long_text, method=ChunkingMethod.RECURSIVE)
        assert len(chunks) > 1
        assert all(len(chunk) <= 1000 for chunk in chunks)
    
    def test_smart_chunking(self) -> None:
        """Test smart chunking methode."""
        long_text = "Dit is een lange tekst.\n\n" * 50  # Met paragraphs
        
        chunks = chunk_text(long_text, method=ChunkingMethod.SMART)
        assert len(chunks) > 0
        assert all(len(chunk) <= 1000 for chunk in chunks)


class TestMerging:
    """Tests voor samenvoegen en ontdubbelen via processors."""
    
    @pytest.mark.asyncio
    async def test_merge_partial_cv_data(self) -> None:
        """Test samenvoegen van partiële CV data via CVProcessor."""
        processor = CVProcessor()
        
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
            phone_number="+31612345678",
            summary="",
            work_experience=[
                WorkExperience(
                    job_title="Junior Developer",
                    company="StartupB",
                    start_date="2018-01-01",
                    end_date="2019-12-31",
                    description="Web development"
                )
            ],
            education=[
                Education(
                    degree="BSc Computer Science",
                    institution="University X",
                    graduation_date="2017-06-01"
                )
            ],
            skills=["React", "Node.js"]
        )
        
        # Merge via processor
        merged = await processor.merge_partial_results([cv1, cv2])
        
        assert merged is not None
        assert merged.full_name == "Jan Jansen"
        assert merged.email == "jan@email.com"
        assert merged.phone_number == "+31612345678"
        assert len(merged.work_experience) == 2
        assert len(merged.education) == 1
        assert len(merged.skills) == 4  # Alle unique skills
    
    @pytest.mark.asyncio
    async def test_merge_partial_invoice_data(self) -> None:
        """Test samenvoegen van partiële invoice data via InvoiceProcessor."""
        processor = InvoiceProcessor()
        
        # Maak twee partiële invoice resultaten
        invoice1 = InvoiceData(
            invoice_id="INV-001",
            invoice_number="INV-001",
            invoice_date="2024-01-01",
            due_date="2024-01-31",
            supplier_name="Bedrijf A",
            supplier_address="",
            supplier_vat_number="NL123456789B01",
            customer_name="Klant B",
            customer_address="",
            customer_vat_number="",
            subtotal=100.0,
            vat_amount=21.0,
            total_amount=121.0,
            currency="EUR",
            line_items=[
                InvoiceLineItem(
                    description="Product 1",
                    quantity=1,
                    unit_price=100.0,
                    line_total=100.0,
                    vat_rate=21.0,
                    vat_amount=21.0
                )
            ]
        )
        
        invoice2 = InvoiceData(
            invoice_id="INV-001",
            invoice_number="",
            invoice_date="",
            due_date="",
            supplier_name="Bedrijf A",
            supplier_address="Straat 1, Amsterdam",
            supplier_vat_number="",
            customer_name="Klant B",
            customer_address="Laan 2, Rotterdam",
            customer_vat_number="NL987654321B01",
            subtotal=50.0,
            vat_amount=10.5,
            total_amount=60.5,
            currency="EUR",
            line_items=[
                InvoiceLineItem(
                    description="Product 2",
                    quantity=1,
                    unit_price=50.0,
                    line_total=50.0,
                    vat_rate=21.0,
                    vat_amount=10.5
                )
            ]
        )
        
        # Merge via processor
        merged = await processor.merge_partial_results([invoice1, invoice2])
        
        assert merged is not None
        assert merged.invoice_number == "INV-001"
        assert merged.supplier_address == "Straat 1, Amsterdam"
        assert merged.customer_address == "Laan 2, Rotterdam"
        assert len(merged.line_items) == 2  # Beide line items
        # Totalen worden herberekend op basis van line items
        assert merged.subtotal == 150.0


class TestValidation:
    """Tests voor data validatie via processors."""
    
    @pytest.mark.asyncio
    async def test_validate_complete_invoice(self) -> None:
        """Test validatie van complete invoice."""
        processor = InvoiceProcessor()
        
        invoice = InvoiceData(
            invoice_id="INV-001",
            invoice_number="INV-001",
            invoice_date="2024-01-01",
            due_date="2024-01-31",
            supplier_name="Bedrijf A",
            supplier_address="Straat 1",
            supplier_vat_number="NL123456789B01",
            customer_name="Klant B",
            customer_address="Laan 2",
            customer_vat_number="NL987654321B01",
            subtotal=100.0,
            vat_amount=21.0,
            total_amount=121.0,
            currency="EUR",
            line_items=[
                InvoiceLineItem(
                    description="Product",
                    quantity=1,
                    unit_price=100.0,
                    line_total=100.0,
                    vat_rate=21.0,
                    vat_amount=21.0
                )
            ]
        )
        
        is_valid, completeness, issues = await processor.validate_extracted_data(invoice)
        
        # Complete invoice moet valid zijn
        assert completeness > 80, f"Expected completeness > 80%, got {completeness}%"
        assert len(issues) == 0 or not is_valid
    
    @pytest.mark.asyncio
    async def test_validate_incomplete_cv(self) -> None:
        """Test validatie van incomplete CV."""
        processor = CVProcessor()
        
        cv = CVData(
            full_name="Jan Jansen",
            email="",
            phone_number="",
            summary="Developer",
            work_experience=[],  # Geen work experience
            education=[],  # Geen education
            skills=[]  # Geen skills
        )
        
        is_valid, completeness, issues = await processor.validate_extracted_data(cv)
        
        # Incomplete CV moet issues hebben
        assert completeness < 100
        assert len(issues) > 0  # Moet issues detecteren


class TestStatistics:
    """Tests voor processor statistics."""
    
    def test_processor_statistics_tracking(self) -> None:
        """Test statistics tracking per processor."""
        processor = InvoiceProcessor()
        
        # Initial stats
        stats = processor.get_statistics()
        assert stats["total_processed"] == 0
        
        # Update stats
        processor.update_statistics(
            success=True,
            processing_time=1.5,
            confidence=85.0,
            completeness=90.0
        )
        
        stats = processor.get_statistics()
        assert stats["total_processed"] == 1
        assert stats["total_successful"] == 1
        assert stats["success_rate"] == 100.0
    
    def test_registry_global_statistics(self) -> None:
        """Test global statistics via registry."""
        registry = ProcessorRegistry()
        invoice_proc = InvoiceProcessor()
        cv_proc = CVProcessor()
        
        registry.register(invoice_proc)
        registry.register(cv_proc)
        
        # Simulate some processing
        invoice_proc.update_statistics(True, 1.0)
        cv_proc.update_statistics(True, 1.5)
        
        global_stats = registry.get_all_statistics()
        
        assert global_stats["total_processors"] == 2
        assert global_stats["global"]["total_documents_processed"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
