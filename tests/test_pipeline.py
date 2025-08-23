"""
Tests voor de verwerkingspijplijn.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import base64

from src.mcp_invoice_processor.processing.pipeline import process_pdf_document, extract_structured_data
from src.mcp_invoice_processor.processing.models import ProcessingResult, CVData, WorkExperience, Education
from src.mcp_invoice_processor.processing.classification import DocumentType


@pytest.fixture
def mock_context():
    """Mock FastMCP context."""
    context = AsyncMock()
    context.info = AsyncMock()
    context.error = AsyncMock()
    return context


@pytest.fixture
def sample_cv_text():
    """Voorbeeld CV tekst voor testing."""
    return """
    Curriculum Vitae
    
    Naam: Jan Jansen
    Email: jan.jansen@email.com
    Telefoon: 06-12345678
    
    Samenvatting:
    Ervaren software ontwikkelaar met expertise in Python en web development.
    
    Werkervaring:
    - Software Engineer bij TechCorp (2020-2023)
    - Junior Developer bij StartupXYZ (2018-2020)
    
    Opleiding:
    - Bachelor Informatica, Universiteit van Amsterdam (2018)
    
    Vaardigheden:
    - Python, JavaScript, React
    - Docker, Kubernetes
    - Agile development
    """


@pytest.fixture
def sample_invoice_text():
    """Voorbeeld factuur tekst voor testing."""
    return """
    FACTUUR
    
    Factuurnummer: INV-2024-001
    Klant: Test Bedrijf BV
    Datum: 15-01-2024
    
    Artikel: Software Licentie
    Prijs: €500,00
    BTW: €105,00
    Totaal: €605,00
    """


class TestDocumentClassification:
    """Tests voor documentclassificatie."""
    
    def test_cv_classification(self, sample_cv_text):
        """Test CV classificatie."""
        from src.mcp_invoice_processor.processing.classification import classify_document
        
        doc_type = classify_document(sample_cv_text)
        assert doc_type == DocumentType.CV
    
    def test_invoice_classification(self, sample_invoice_text):
        """Test factuur classificatie."""
        from src.mcp_invoice_processor.processing.classification import classify_document
        
        doc_type = classify_document(sample_invoice_text)
        assert doc_type == DocumentType.INVOICE


class TestTextExtraction:
    """Tests voor tekstextractie."""
    
    def test_text_extraction_success(self):
        """Test succesvolle tekstextractie."""
        from src.mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf
        
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
    
    def test_recursive_chunking(self):
        """Test recursive chunking methode."""
        from src.mcp_invoice_processor.processing.chunking import chunk_text, ChunkingMethod
        
        long_text = "Dit is een lange tekst. " * 100  # 2000+ karakters
        
        chunks = chunk_text(long_text, method=ChunkingMethod.RECURSIVE)
        assert len(chunks) > 1
        assert all(len(chunk) <= 1000 for chunk in chunks)


class TestMerging:
    """Tests voor samenvoegen en ontdubbelen."""
    
    def test_merge_partial_cv_data(self):
        """Test samenvoegen van partiële CV data."""
        from src.mcp_invoice_processor.processing.merging import merge_partial_cv_data
        
        # Maak twee partiële CV resultaten
        cv1 = CVData(
            full_name="Jan Jansen",
            email="jan@email.com",
            summary="Software ontwikkelaar",
            work_experience=[
                WorkExperience(
                    job_title="Software Engineer",
                    company="TechCorp",
                    description="Python development"
                )
            ],
            education=[],
            skills=["Python", "JavaScript"]
        )
        
        cv2 = CVData(
            full_name="Jan Jansen",
            phone_number="06-12345678",
            summary="Software ontwikkelaar",
            work_experience=[
                WorkExperience(
                    job_title="Software Engineer",
                    company="TechCorp",
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


class TestPipeline:
    """Tests voor de hoofdpijplijn."""
    
    @pytest.mark.asyncio
    async def test_process_pdf_document_success(self, mock_context, sample_cv_text):
        """Test succesvolle documentverwerking."""
        with patch('src.mcp_invoice_processor.processing.text_extractor.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = sample_cv_text
            
            with patch('src.mcp_invoice_processor.processing.pipeline.extract_structured_data') as mock_extract_data:
                mock_cv = CVData(
                    full_name="Jan Jansen",
                    email="jan@email.com",
                    summary="Software ontwikkelaar",
                    work_experience=[],
                    education=[],
                    skills=[]
                )
                mock_extract_data.return_value = mock_cv
                
                # Mock PDF bytes
                pdf_bytes = b"%PDF-1.4\n%Test PDF content"
                
                result = await process_pdf_document(pdf_bytes, "test.pdf", mock_context)
                
                assert result.status == "success"
                assert result.document_type == "cv"
                assert result.data is not None
                assert isinstance(result.data, CVData)
    
    @pytest.mark.asyncio
    async def test_process_pdf_document_extraction_error(self, mock_context):
        """Test foutafhandeling bij tekstextractie."""
        with patch('src.mcp_invoice_processor.processing.text_extractor.extract_text_from_pdf') as mock_extract:
            mock_extract.side_effect = ValueError("PDF corrupt")
            
            pdf_bytes = b"invalid pdf content"
            result = await process_pdf_document(pdf_bytes, "test.pdf", mock_context)
            
            assert result.status == "error"
            assert "PDF corrupt" in result.error_message


class TestOllamaIntegration:
    """Tests voor Ollama integratie."""
    
    @pytest.mark.asyncio
    async def test_extract_structured_data_success(self, mock_context):
        """Test succesvolle data-extractie via Ollama."""
        with patch('ollama.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = {
                'message': {
                    'content': '{"full_name": "Jan Jansen", "email": "jan@email.com", "summary": "Developer", "work_experience": [], "education": [], "skills": []}'
                }
            }
            mock_client.chat.return_value = mock_response
            
            result = await extract_structured_data(
                "Test CV tekst", 
                DocumentType.CV, 
                mock_context
            )
            
            assert result is not None
            assert isinstance(result, CVData)
            assert result.full_name == "Jan Jansen"
    
    @pytest.mark.asyncio
    async def test_extract_structured_data_validation_error(self, mock_context):
        """Test foutafhandeling bij validatiefouten."""
        with patch('ollama.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock een ongeldige JSON response
            mock_response = {
                'message': {
                    'content': '{"invalid": "json"}'
                }
            }
            mock_client.chat.return_value = mock_response
            
            result = await extract_structured_data(
                "Test tekst", 
                DocumentType.CV, 
                mock_context
            )
            
            assert result is None
            mock_context.error.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
