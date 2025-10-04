#!/usr/bin/env python3
"""
Debug script om Amazon factuur tekst te bekijken met v2.0 processors.
"""

import asyncio
from pathlib import Path

from mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf
from mcp_invoice_processor.processors import get_registry
from mcp_invoice_processor.processors.invoice import InvoiceProcessor


async def debug_amazon_invoice() -> None:
    """Debug Amazon factuur classificatie met v2.0."""
    print("=== Amazon Factuur Debug (v2.0) ===")
    
    pdf_file = "amazon_rugtas-factuur.pdf"
    
    if not Path(pdf_file).exists():
        print(f"❌ PDF bestand niet gevonden: {pdf_file}")
        return
    
    try:
        # PDF inlezen en tekst extraheren
        with open(pdf_file, 'rb') as f:
            pdf_bytes = f.read()
        
        text = extract_text_from_pdf(pdf_bytes)
        print(f"PDF grootte: {len(pdf_bytes)} bytes")
        print(f"Tekst lengte: {len(text)} karakters")
        
        # Toon volledige tekst
        print("\n=== VOLLEDIGE TEKST ===")
        print(text)
        print("=== EINDE TEKST ===\n")
        
        # Test classificatie via registry (parallel)
        registry = get_registry()
        doc_type, confidence, processor = await registry.classify_document(text, None)
        print(f"Gedetecteerd type: {doc_type}")
        print(f"Confidence: {confidence:.1f}%")
        print(f"Processor: {processor.tool_name if processor else 'None'}")
        
        # Analyseer trefwoorden per processor
        invoice_proc = InvoiceProcessor()
        invoice_confidence = await invoice_proc.classify(text, None)
        
        print(f"\nInvoice processor confidence: {invoice_confidence:.1f}%")
        print(f"Invoice keywords: {len(invoice_proc.classification_keywords)}")
        
        # Toon welke keywords gevonden zijn
        text_lower = text.lower()
        found_keywords = [kw for kw in invoice_proc.classification_keywords if kw in text_lower]
        print(f"Gevonden keywords ({len(found_keywords)}): {', '.join(sorted(found_keywords))}")
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_amazon_invoice())
