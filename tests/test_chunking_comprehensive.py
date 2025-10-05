#!/usr/bin/env python3
"""
Uitgebreide test suite voor chunking functionaliteit.
Test alle chunking methoden, auto mode, en edge cases.
"""

import os
import pytest
import logging
from unittest.mock import patch
from src.mcp_invoice_processor.processing.chunking import (
    chunk_text, 
    ChunkingMethod, 
    get_ollama_model_context_size, 
    calculate_auto_chunk_size
)
from src.mcp_invoice_processor.config import settings

# Setup logging voor tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestChunkingBasic:
    """Basis tests voor chunking functionaliteit."""
    
    def test_recursive_chunking_default(self):
        """Test recursive chunking met default instellingen."""
        long_text = "Dit is een test zin. " * 100  # ~2000 karakters
        
        chunks = chunk_text(long_text, method=ChunkingMethod.RECURSIVE)
        
        assert len(chunks) > 1, "Moet meerdere chunks produceren"
        assert all(len(chunk) <= 1000 for chunk in chunks), "Alle chunks moeten <= 1000 karakters zijn"
        assert all(len(chunk) > 0 for chunk in chunks), "Alle chunks moeten niet-leeg zijn"
        
        # Controleer overlap
        for i in range(len(chunks) - 1):
            overlap_found = False
            for j in range(min(200, len(chunks[i]))):
                if chunks[i][-j:] in chunks[i+1][:j+200]:
                    overlap_found = True
                    break
            assert overlap_found, f"Geen overlap gevonden tussen chunk {i} en {i+1}"
    
    def test_smart_chunking_default(self):
        """Test smart chunking met default instellingen."""
        long_text = "Dit is een paragraaf.\n\nDit is een andere paragraaf.\n\n" * 50
        
        chunks = chunk_text(long_text, method=ChunkingMethod.SMART)
        
        assert len(chunks) > 0, "Moet chunks produceren"
        assert all(len(chunk) <= 1000 for chunk in chunks), "Alle chunks moeten <= 1000 karakters zijn"
        assert all(len(chunk) > 0 for chunk in chunks), "Alle chunks moeten niet-leeg zijn"
    
    def test_custom_chunk_size(self):
        """Test custom chunk size."""
        long_text = "Dit is een test zin. " * 100
        
        # Test verschillende chunk sizes
        for chunk_size in [500, 1500, 2000]:
            chunks = chunk_text(long_text, chunk_size=chunk_size)
            assert len(chunks) > 0, f"Moet chunks produceren voor size {chunk_size}"
            assert all(len(chunk) <= chunk_size for chunk in chunks), f"Alle chunks moeten <= {chunk_size} zijn"
    
    def test_chunk_overlap(self):
        """Test chunk overlap functionaliteit."""
        long_text = "Dit is een test zin. " * 100
        
        # Test verschillende overlaps
        for overlap in [100, 300, 500]:
            chunks = chunk_text(long_text, chunk_size=1000, chunk_overlap=overlap)
            assert len(chunks) > 0, f"Moet chunks produceren voor overlap {overlap}"
            
            # Controleer dat overlap ongeveer klopt
            for i in range(len(chunks) - 1):
                # Zoek overlap tussen chunks
                overlap_found = False
                for j in range(min(overlap + 50, len(chunks[i]))):
                    if chunks[i][-j:] in chunks[i+1][:j+overlap+50]:
                        overlap_found = True
                        break
                assert overlap_found, f"Geen overlap gevonden tussen chunk {i} en {i+1}"


class TestChunkingValidation:
    """Tests voor validatie en error handling."""
    
    def test_invalid_chunk_size_too_small(self):
        """Test validatie van te kleine chunk size."""
        long_text = "Test tekst"
        
        with pytest.raises(ValueError, match="moet minimaal 100 zijn"):
            chunk_text(long_text, chunk_size=50)
    
    def test_invalid_chunk_size_too_large(self):
        """Test validatie van te grote chunk size."""
        long_text = "Test tekst"
        
        with pytest.raises(ValueError, match="mag maximaal 4000 zijn"):
            chunk_text(long_text, chunk_size=5000)
    
    def test_invalid_chunk_overlap(self):
        """Test validatie van te grote overlap."""
        long_text = "Test tekst"
        
        with pytest.raises(ValueError, match="chunk_overlap moet kleiner zijn dan chunk_size"):
            chunk_text(long_text, chunk_size=1000, chunk_overlap=1000)
    
    def test_empty_text(self):
        """Test chunking van lege tekst."""
        chunks = chunk_text("")
        assert chunks == [], "Lege tekst moet lege lijst produceren"
    
    def test_short_text(self):
        """Test chunking van korte tekst."""
        short_text = "Dit is een korte tekst."
        chunks = chunk_text(short_text, chunk_size=1000)
        
        assert len(chunks) == 1, "Korte tekst moet één chunk produceren"
        assert chunks[0] == short_text, "Chunk moet originele tekst bevatten"


class TestAutoMode:
    """Tests voor auto mode functionaliteit."""
    
    @patch('src.mcp_invoice_processor.processing.chunking.ollama.show')
    def test_get_ollama_model_context_size_known_model(self, mock_show):
        """Test ophalen context size voor bekend model."""
        # Mock response voor bekend model
        mock_show.return_value = {
            'details': {
                'parameter_size': '7B'
            }
        }
        
        context_size = get_ollama_model_context_size("llama3:8b")
        
        assert context_size == 8192, "Bekend model moet juiste context size retourneren"
        mock_show.assert_called_once_with("llama3:8b")
    
    @patch('src.mcp_invoice_processor.processing.chunking.ollama.show')
    def test_get_ollama_model_context_size_unknown_model(self, mock_show):
        """Test ophalen context size voor onbekend model."""
        # Mock response voor onbekend model
        mock_show.return_value = {
            'details': {
                'parameter_size': 'Unknown'
            }
        }
        
        context_size = get_ollama_model_context_size("unknown-model")
        
        assert context_size == 8192, "Onbekend model moet fallback context size retourneren"
    
    @patch('src.mcp_invoice_processor.processing.chunking.ollama.show')
    def test_get_ollama_model_context_size_error(self, mock_show):
        """Test error handling bij ophalen model info."""
        # Mock error
        mock_show.side_effect = Exception("Connection error")
        
        context_size = get_ollama_model_context_size("test-model")
        
        assert context_size == 8192, "Error moet fallback context size retourneren"
    
    @patch('src.mcp_invoice_processor.processing.chunking.get_ollama_model_context_size')
    def test_calculate_auto_chunk_size(self, mock_get_context):
        """Test berekening auto chunk size."""
        # Mock context size
        mock_get_context.return_value = 8192  # 8K tokens
        
        chunk_size = calculate_auto_chunk_size("test-model")
        
        # 8192 tokens * 4 chars/token * 0.8 safety = 26214 chars
        # Minus default overlap (200) = 26014 chars
        # Maar dit wordt beperkt door MAX_CHUNK_SIZE (4000)
        expected_size = min(int(8192 * 4 * 0.8) - settings.chunking.DEFAULT_CHUNK_OVERLAP, 
                           settings.chunking.MAX_CHUNK_SIZE)
        assert chunk_size == expected_size, f"Auto chunk size moet {expected_size} zijn"
        mock_get_context.assert_called_once_with("test-model")
    
    @patch('src.mcp_invoice_processor.processing.chunking.get_ollama_model_context_size')
    def test_calculate_auto_chunk_size_with_custom_overlap(self, mock_get_context):
        """Test berekening auto chunk size met custom overlap."""
        # Mock context size
        mock_get_context.return_value = 8192  # 8K tokens
        
        custom_overlap = 500
        chunk_size = calculate_auto_chunk_size("test-model", chunk_overlap=custom_overlap)
        
        # 8192 tokens * 4 chars/token * 0.8 safety = 26214 chars
        # Minus custom overlap (500) = 25714 chars
        # Maar dit wordt beperkt door MAX_CHUNK_SIZE (4000)
        expected_size = min(int(8192 * 4 * 0.8) - custom_overlap, 
                           settings.chunking.MAX_CHUNK_SIZE)
        assert chunk_size == expected_size, f"Auto chunk size moet {expected_size} zijn"
        mock_get_context.assert_called_once_with("test-model")
    
    @patch('src.mcp_invoice_processor.processing.chunking.get_ollama_model_context_size')
    def test_calculate_auto_chunk_size_with_limits(self, mock_get_context):
        """Test auto chunk size met configuratie limits."""
        # Mock zeer grote context size
        mock_get_context.return_value = 100000  # 100K tokens
        
        chunk_size = calculate_auto_chunk_size("test-model")
        
        # Moet beperkt worden door MAX_CHUNK_SIZE
        assert chunk_size == settings.chunking.MAX_CHUNK_SIZE, "Moet beperkt worden door MAX_CHUNK_SIZE"
    
    @patch('src.mcp_invoice_processor.processing.chunking.get_ollama_model_context_size')
    def test_calculate_auto_chunk_size_disabled(self, mock_get_context):
        """Test auto chunk size wanneer uitgeschakeld."""
        # Mock context size
        mock_get_context.return_value = 8192
        
        # Disable auto mode
        with patch.object(settings.chunking, 'AUTO_MODE_ENABLED', False):
            chunk_size = calculate_auto_chunk_size("test-model")
        
        assert chunk_size == settings.chunking.DEFAULT_CHUNK_SIZE, "Moet default chunk size gebruiken"
        mock_get_context.assert_not_called()
    
    @patch('src.mcp_invoice_processor.processing.chunking.calculate_auto_chunk_size')
    def test_chunk_text_auto_mode(self, mock_calculate):
        """Test chunk_text met auto mode."""
        mock_calculate.return_value = 2000
        
        long_text = "Dit is een test zin. " * 100
        
        chunks = chunk_text(long_text, method=ChunkingMethod.AUTO, chunk_overlap=300)
        
        assert len(chunks) > 0, "Moet chunks produceren"
        assert all(len(chunk) <= 2000 for chunk in chunks), "Alle chunks moeten <= auto chunk size zijn"
        mock_calculate.assert_called_once_with(chunk_overlap=300)
    
    def test_chunk_text_auto_string(self):
        """Test chunk_text met 'auto' string parameter."""
        long_text = "Dit is een test zin. " * 100
        
        with patch('src.mcp_invoice_processor.processing.chunking.calculate_auto_chunk_size') as mock_calculate:
            mock_calculate.return_value = 1500
            
            chunks = chunk_text(long_text, chunk_size="auto", chunk_overlap=400)
            
            assert len(chunks) > 0, "Moet chunks produceren"
            assert all(len(chunk) <= 1500 for chunk in chunks), "Alle chunks moeten <= auto chunk size zijn"
            mock_calculate.assert_called_once_with(chunk_overlap=400)


class TestChunkingEdgeCases:
    """Tests voor edge cases en speciale situaties."""
    
    def test_very_long_single_word(self):
        """Test chunking van zeer lang woord."""
        long_word = "a" * 5000
        chunks = chunk_text(long_word, chunk_size=1000)
        
        assert len(chunks) > 0, "Moet chunks produceren"
        assert all(len(chunk) <= 1000 for chunk in chunks), "Alle chunks moeten <= chunk size zijn"
    
    def test_text_with_special_characters(self):
        """Test chunking van tekst met speciale karakters."""
        special_text = "Test met émojis 🎉 en speciale karakters: àáâãäåæçèéêë" * 50
        
        chunks = chunk_text(special_text, method=ChunkingMethod.RECURSIVE)
        
        assert len(chunks) > 0, "Moet chunks produceren"
        assert all(len(chunk) <= 1000 for chunk in chunks), "Alle chunks moeten <= chunk size zijn"
        
        # Controleer dat speciale karakters behouden blijven
        combined_text = "".join(chunks)
        assert "🎉" in combined_text, "Emoji moet behouden blijven"
        assert "àáâãäåæçèéêë" in combined_text, "Speciale karakters moeten behouden blijven"
    
    def test_text_with_newlines(self):
        """Test chunking van tekst met veel newlines."""
        newline_text = "Regel 1\nRegel 2\nRegel 3\n" * 100
        
        chunks = chunk_text(newline_text, method=ChunkingMethod.SMART)
        
        assert len(chunks) > 0, "Moet chunks produceren"
        assert all(len(chunk) <= 1000 for chunk in chunks), "Alle chunks moeten <= chunk size zijn"
    
    def test_text_with_tabs_and_spaces(self):
        """Test chunking van tekst met tabs en spaties."""
        tab_text = "Tekst\tmet\ttabs\t\t\t" + " " * 100 + "en veel spaties" * 50
        
        chunks = chunk_text(tab_text, method=ChunkingMethod.RECURSIVE)
        
        assert len(chunks) > 0, "Moet chunks produceren"
        assert all(len(chunk) <= 1000 for chunk in chunks), "Alle chunks moeten <= chunk size zijn"


class TestChunkingPerformance:
    """Tests voor performance en grote documenten."""
    
    def test_large_document_chunking(self):
        """Test chunking van groot document."""
        # Maak groot document (100KB)
        large_text = "Dit is een grote test zin met veel content. " * 2500
        
        chunks = chunk_text(large_text, chunk_size=2000)
        
        assert len(chunks) > 0, "Moet chunks produceren"
        assert all(len(chunk) <= 2000 for chunk in chunks), "Alle chunks moeten <= chunk size zijn"
        
        # Controleer dat chunks niet leeg zijn en content bevatten
        assert all(len(chunk) > 0 for chunk in chunks), "Alle chunks moeten niet-leeg zijn"
        assert all("Dit is een grote test zin" in chunk for chunk in chunks), "Alle chunks moeten test content bevatten"
    
    def test_chunking_consistency(self):
        """Test dat chunking consistent is."""
        text = "Dit is een test tekst voor consistentie. " * 100
        
        # Chunk meerdere keren
        chunks1 = chunk_text(text, chunk_size=1000)
        chunks2 = chunk_text(text, chunk_size=1000)
        
        assert chunks1 == chunks2, "Chunking moet consistent zijn"
    
    def test_different_methods_same_result(self):
        """Test dat verschillende methoden vergelijkbare resultaten geven."""
        text = "Dit is een test tekst. " * 100
        
        chunks_recursive = chunk_text(text, method=ChunkingMethod.RECURSIVE, chunk_size=1000)
        chunks_smart = chunk_text(text, method=ChunkingMethod.SMART, chunk_size=1000)
        
        # Beide moeten chunks produceren
        assert len(chunks_recursive) > 0, "Recursive moet chunks produceren"
        assert len(chunks_smart) > 0, "Smart moet chunks produceren"
        
        # Beide moeten binnen chunk size blijven
        assert all(len(chunk) <= 1000 for chunk in chunks_recursive), "Recursive chunks moeten <= 1000 zijn"
        assert all(len(chunk) <= 1000 for chunk in chunks_smart), "Smart chunks moeten <= 1000 zijn"


class TestChunkingIntegration:
    """Integration tests voor chunking met andere componenten."""
    
    def test_chunking_with_configuration(self):
        """Test chunking met verschillende configuraties."""
        text = "Test tekst voor configuratie. " * 100
        
        # Test met verschillende configuraties
        test_configs = [
            (500, 100),
            (1500, 300),
            (2000, 400),
        ]
        
        for chunk_size, chunk_overlap in test_configs:
            chunks = chunk_text(
                text, 
                method=ChunkingMethod.RECURSIVE,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            assert len(chunks) > 0, f"Moet chunks produceren voor chunk_size={chunk_size}, overlap={chunk_overlap}"
            assert all(len(chunk) <= chunk_size for chunk in chunks), f"Chunks moeten <= {chunk_size} zijn"
    
    def test_chunking_with_environment_variables(self):
        """Test chunking met environment variables."""
        text = "Test tekst voor environment variables. " * 100
        
        # Set environment variables
        os.environ["CHUNKING_DEFAULT_CHUNK_SIZE"] = "1500"
        os.environ["CHUNKING_DEFAULT_CHUNK_OVERLAP"] = "300"
        
        try:
            # Herlaad configuratie
            from src.mcp_invoice_processor.config import AppSettings
            AppSettings()  # Herlaad configuratie
            
            chunks = chunk_text(text)
            
            assert len(chunks) > 0, "Moet chunks produceren"
            assert all(len(chunk) <= 1500 for chunk in chunks), "Chunks moeten <= 1500 zijn"
            
        finally:
            # Cleanup
            del os.environ["CHUNKING_DEFAULT_CHUNK_SIZE"]
            del os.environ["CHUNKING_DEFAULT_CHUNK_OVERLAP"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
