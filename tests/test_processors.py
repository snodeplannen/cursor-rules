"""
Tests voor de nieuwe modulaire processor architecture.

Test de BaseDocumentProcessor, ProcessorRegistry, InvoiceProcessor en CVProcessor.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from mcp_invoice_processor.processors import (
    get_registry,
    register_processor,
    BaseDocumentProcessor,
    ProcessorRegistry,
)
from mcp_invoice_processor.processors.invoice import InvoiceProcessor
from mcp_invoice_processor.processors.cv import CVProcessor


class TestProcessorRegistry:
    """Test de ProcessorRegistry functionaliteit."""
    
    def test_registry_singleton(self):
        """Test dat get_registry altijd dezelfde instance teruggeeft."""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2
    
    def test_register_processor(self):
        """Test processor registratie."""
        registry = ProcessorRegistry()
        invoice_processor = InvoiceProcessor()
        
        registry.register(invoice_processor)
        
        assert "invoice" in registry.get_processor_types()
        assert registry.get_processor("invoice") is invoice_processor
    
    def test_register_duplicate_raises_error(self):
        """Test dat dubbele registratie een error geeft."""
        registry = ProcessorRegistry()
        invoice_processor1 = InvoiceProcessor()
        invoice_processor2 = InvoiceProcessor()
        
        registry.register(invoice_processor1)
        
        with pytest.raises(ValueError, match="al geregistreerd"):
            registry.register(invoice_processor2)
    
    def test_get_all_processors(self):
        """Test ophalen van alle processors."""
        registry = ProcessorRegistry()
        invoice_processor = InvoiceProcessor()
        cv_processor = CVProcessor()
        
        registry.register(invoice_processor)
        registry.register(cv_processor)
        
        processors = registry.get_all_processors()
        assert len(processors) == 2
        assert invoice_processor in processors
        assert cv_processor in processors


class TestInvoiceProcessor:
    """Test de InvoiceProcessor."""
    
    def test_metadata_properties(self):
        """Test processor metadata."""
        processor = InvoiceProcessor()
        
        assert processor.document_type == "invoice"
        assert processor.display_name == "Factuur"
        assert processor.tool_name == "process_invoice"
        assert "facturen" in processor.tool_description.lower()
    
    def test_classification_keywords(self):
        """Test invoice classificatie keywords."""
        processor = InvoiceProcessor()
        keywords = processor.classification_keywords
        
        # Check voor essentiële invoice keywords
        assert "factuur" in keywords
        assert "invoice" in keywords
        assert "btw" in keywords
        assert "totaal" in keywords
        assert len(keywords) > 20  # Moet veel keywords hebben
    
    @pytest.mark.asyncio
    async def test_classify_invoice_text(self):
        """Test classificatie van invoice tekst."""
        processor = InvoiceProcessor()
        
        invoice_text = """
        FACTUUR #123
        Datum: 2024-01-01
        
        Van: Bedrijf A
        BTW: NL123456789B01
        
        Aan: Klant B
        
        Artikel         Aantal  Prijs   Totaal
        Product 1       2       €10     €20
        
        Subtotaal: €20
        BTW (21%): €4.20
        Totaal: €24.20
        """
        
        confidence = await processor.classify(invoice_text)
        
        # Moet hoge confidence hebben voor invoice
        assert confidence > 50, f"Expected high confidence for invoice, got {confidence}"
    
    @pytest.mark.asyncio
    async def test_classify_non_invoice_text(self):
        """Test classificatie van niet-invoice tekst."""
        processor = InvoiceProcessor()
        
        other_text = """
        Curriculum Vitae
        
        Naam: John Doe
        Ervaring:
        - Software Developer bij TechCorp
        
        Vaardigheden:
        - Python
        - JavaScript
        """
        
        confidence = await processor.classify(other_text)
        
        # Moet lage confidence hebben voor CV tekst
        assert confidence < 50, f"Expected low confidence for CV text, got {confidence}"
    
    def test_data_model(self):
        """Test dat data model correct is."""
        processor = InvoiceProcessor()
        
        from mcp_invoice_processor.processors.invoice.models import InvoiceData
        assert processor.data_model == InvoiceData
    
    def test_json_schema(self):
        """Test JSON schema generatie."""
        processor = InvoiceProcessor()
        schema = processor.get_json_schema()
        
        assert "properties" in schema
        assert "invoice_id" in schema["properties"]
        assert "total_amount" in schema["properties"]
        assert "line_items" in schema["properties"]
    
    def test_extraction_prompts(self):
        """Test prompt generatie."""
        processor = InvoiceProcessor()
        
        text = "Test invoice text"
        
        json_schema_prompt = processor.get_extraction_prompt(text, "json_schema")
        assert "Extract" in json_schema_prompt
        assert "invoice" in json_schema_prompt.lower()
        assert text in json_schema_prompt
        
        prompt_parsing_prompt = processor.get_extraction_prompt(text, "prompt_parsing")
        assert "JSON" in prompt_parsing_prompt
        assert text in prompt_parsing_prompt


class TestCVProcessor:
    """Test de CVProcessor."""
    
    def test_metadata_properties(self):
        """Test processor metadata."""
        processor = CVProcessor()
        
        assert processor.document_type == "cv"
        assert processor.display_name == "Curriculum Vitae"
        assert processor.tool_name == "process_cv"
        assert "cv" in processor.tool_description.lower()
    
    def test_classification_keywords(self):
        """Test CV classificatie keywords."""
        processor = CVProcessor()
        keywords = processor.classification_keywords
        
        # Check voor essentiële CV keywords
        assert "ervaring" in keywords
        assert "opleiding" in keywords
        assert "vaardigheden" in keywords
        assert "education" in keywords
        assert len(keywords) > 15  # Moet genoeg keywords hebben
    
    @pytest.mark.asyncio
    async def test_classify_cv_text(self):
        """Test classificatie van CV tekst."""
        processor = CVProcessor()
        
        cv_text = """
        Curriculum Vitae
        
        Naam: Jane Doe
        Email: jane@example.com
        
        Werkervaring:
        - Senior Developer bij TechCorp (2020-2023)
        - Junior Developer bij StartupB (2018-2020)
        
        Opleiding:
        - MSc Computer Science, University X
        
        Vaardigheden:
        - Python, Java, JavaScript
        - Machine Learning
        """
        
        confidence = await processor.classify(cv_text)
        
        # Moet hoge confidence hebben voor CV
        assert confidence >= 50, f"Expected high confidence for CV, got {confidence}"
    
    @pytest.mark.asyncio
    async def test_classify_non_cv_text(self):
        """Test classificatie van niet-CV tekst."""
        processor = CVProcessor()
        
        invoice_text = """
        FACTUUR #123
        
        Totaalbedrag: €500
        BTW: €105
        """
        
        confidence = await processor.classify(invoice_text)
        
        # Moet lage confidence hebben voor invoice tekst
        assert confidence < 50, f"Expected low confidence for invoice text, got {confidence}"
    
    def test_data_model(self):
        """Test dat data model correct is."""
        processor = CVProcessor()
        
        from mcp_invoice_processor.processors.cv.models import CVData
        assert processor.data_model == CVData
    
    def test_json_schema(self):
        """Test JSON schema generatie."""
        processor = CVProcessor()
        schema = processor.get_json_schema()
        
        assert "properties" in schema
        assert "full_name" in schema["properties"]
        assert "work_experience" in schema["properties"]
        assert "skills" in schema["properties"]


class TestParallelClassification:
    """Test async parallel classificatie."""
    
    @pytest.mark.asyncio
    async def test_classify_document_parallel(self):
        """Test dat classificatie parallel uitgevoerd wordt."""
        registry = ProcessorRegistry()
        registry.register(InvoiceProcessor())
        registry.register(CVProcessor())
        
        invoice_text = """
        FACTUUR #123
        Datum: 2024-01-01
        Totaal: €100
        BTW: €21
        """
        
        doc_type, confidence, processor = await registry.classify_document(invoice_text)
        
        assert doc_type == "invoice"
        assert processor is not None
        assert processor.document_type == "invoice"
        assert confidence > 0
    
    @pytest.mark.asyncio
    async def test_classify_unknown_document(self):
        """Test classificatie van onbekend document."""
        registry = ProcessorRegistry()
        registry.register(InvoiceProcessor())
        registry.register(CVProcessor())
        
        unknown_text = "This is just some random text with no specific document markers."
        
        doc_type, confidence, processor = await registry.classify_document(unknown_text)
        
        # Zou lage confidence moeten hebben
        assert confidence < 20 or doc_type == "unknown"


class TestStatistics:
    """Test statistics tracking."""
    
    def test_initial_statistics(self):
        """Test initiële statistics."""
        processor = InvoiceProcessor()
        stats = processor.get_statistics()
        
        assert stats["total_processed"] == 0
        assert stats["total_successful"] == 0
        assert stats["total_failed"] == 0
        assert stats["success_rate"] == 0.0
    
    def test_update_statistics(self):
        """Test statistics updaten."""
        processor = InvoiceProcessor()
        
        processor.update_statistics(
            success=True,
            processing_time=1.5,
            confidence=85.0,
            completeness=95.0
        )
        
        stats = processor.get_statistics()
        
        assert stats["total_processed"] == 1
        assert stats["total_successful"] == 1
        assert stats["total_failed"] == 0
        assert stats["success_rate"] == 100.0
        assert stats["avg_processing_time"] == 1.5
        assert stats["avg_confidence"] == 85.0
        assert stats["avg_completeness"] == 95.0
    
    def test_registry_global_statistics(self):
        """Test global statistics van registry."""
        registry = ProcessorRegistry()
        invoice_proc = InvoiceProcessor()
        cv_proc = CVProcessor()
        
        registry.register(invoice_proc)
        registry.register(cv_proc)
        
        # Update some stats
        invoice_proc.update_statistics(True, 1.0)
        invoice_proc.update_statistics(True, 2.0)
        cv_proc.update_statistics(True, 1.5)
        
        global_stats = registry.get_all_statistics()
        
        assert global_stats["total_processors"] == 2
        assert global_stats["global"]["total_documents_processed"] == 3
        assert global_stats["global"]["total_successful"] == 3
        assert "invoice" in global_stats["processors"]
        assert "cv" in global_stats["processors"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

