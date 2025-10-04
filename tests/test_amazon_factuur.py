"""
Test van Amazon rugtas factuur PDF verwerking met nieuwe processor architecture.

Updated voor v2.0 modulaire processors.
"""

import asyncio
import sys
import os
import pytest
from typing import List, Optional, Dict, Any
from unittest.mock import MagicMock

from fastmcp import Context, FastMCP
from mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf
from mcp_invoice_processor.processors import get_registry

# Voeg src directory toe aan Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


class MockContext(Context):
    """Mock context voor testing die ECHT compatible is met FastMCP Context."""
    
    def __init__(self) -> None:
        # Maak een mock FastMCP instance
        mock_fastmcp = MagicMock(spec=FastMCP)
        super().__init__(mock_fastmcp)
        self.info_calls: List[str] = []
        self.error_calls: List[str] = []
        self.warning_calls: List[str] = []
        self.debug_calls: List[str] = []
    
    async def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Mock info methode."""
        self.info_calls.append(message)
        print(f"INFO: {message}")
    
    async def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Mock error methode."""
        self.error_calls.append(message)
        print(f"ERROR: {message}")
    
    async def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Mock warning methode."""
        self.warning_calls.append(message)
        print(f"WARNING: {message}")
    
    async def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Mock debug methode."""
        self.debug_calls.append(message)
        print(f"DEBUG: {message}")
    
    async def report_progress(self, progress: float, total: float = 100) -> None:
        """Mock progress methode."""
        print(f"PROGRESS: {progress}/{total}")


@pytest.mark.asyncio
@pytest.mark.ollama
@pytest.mark.integration
async def test_amazon_invoice() -> None:
    """Test Amazon rugtas factuur verwerking met nieuwe processor.
    
    Deze test maakt ECHTE Ollama calls (niet gemockt).
    Vereist Ollama running op localhost:11434.
    """
    print("=== Amazon Rugtas Factuur Verwerking Test (v2.0) ===")
    
    pdf_file = "amazon_rugtas-factuur.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF bestand niet gevonden: {pdf_file}")
        pytest.skip(f"PDF bestand niet gevonden: {pdf_file}")
    
    try:
        # Stap 1: PDF inlezen
        print(f"\n1. PDF Bestand Inlezen: {pdf_file}")
        with open(pdf_file, 'rb') as f:
            pdf_bytes = f.read()
        print(f"   PDF grootte: {len(pdf_bytes)} bytes")
        
        # Stap 2: Tekst extraheren
        print("\n2. Tekst Extractie uit PDF:")
        text = extract_text_from_pdf(pdf_bytes)
        print(f"   Geëxtraheerde tekst lengte: {len(text)} karakters")
        print(f"   Eerste 200 karakters: {text[:200]}...")
        
        # Stap 3: Document classificatie via registry (parallel!)
        print("\n3. Document Classificatie (v2.0 - Parallel):")
        registry = get_registry()
        ctx = MockContext()
        
        doc_type, confidence, processor = await registry.classify_document(text, ctx)
        print(f"   Gedetecteerd type: {doc_type}")
        print(f"   Confidence: {confidence:.1f}%")
        print(f"   Processor: {processor.tool_name if processor else 'None'}")
        
        # Stap 4: Gestructureerde data extractie via processor
        print("\n4. Gestructureerde Data Extractie (v2.0):")
        
        if processor:
            result = await processor.extract(text, ctx, method="hybrid")
            
            if result:
                print("   ✅ Extractie succesvol!")
                print(f"   Type: {type(result).__name__}")
                
                # Toon factuur details
                if hasattr(result, 'invoice_number'):
                    print(f"   Factuurnummer: {result.invoice_number}")
                if hasattr(result, 'supplier_name'):
                    print(f"   Leverancier: {result.supplier_name}")
                if hasattr(result, 'total_amount'):
                    print(f"   Totaalbedrag: €{result.total_amount}")
                if hasattr(result, 'line_items'):
                    print(f"   Aantal producten: {len(result.line_items)}")
                    for i, item in enumerate(result.line_items[:5]):  # Toon eerste 5
                        print(f"     {i+1}. {item.description} - {item.quantity}x €{item.unit_price} = €{item.line_total}")
                    if len(result.line_items) > 5:
                        print(f"     ... en {len(result.line_items) - 5} meer items")
                
                # Validatie
                is_valid, completeness, issues = await processor.validate_extracted_data(result, ctx)
                print("\n   Validatie:")
                print(f"   - Valid: {is_valid}")
                print(f"   - Completeness: {completeness:.1f}%")
                if issues:
                    print(f"   - Issues: {', '.join(issues)}")
                
                # Custom metrics
                metrics = await processor.get_custom_metrics(result, ctx)
                print("\n   Metrics:")
                for key, value in metrics.items():
                    print(f"   - {key}: {value}")
                
            else:
                print("   ❌ Extractie mislukt")
        else:
            print("   ❌ Geen geschikte processor gevonden")
        
        # Context calls tonen
        print("\n5. Context Calls:")
        print(f"   Info: {len(ctx.info_calls)}")
        print(f"   Debug: {len(ctx.debug_calls)}")
        print(f"   Warning: {len(ctx.warning_calls)}")
        print(f"   Error: {len(ctx.error_calls)}")
        
    except Exception as e:
        print(f"❌ Fout bij verwerking: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(test_amazon_invoice())

