#!/usr/bin/env python3
"""
Debug script om Amazon factuur tekst te bekijken en classificatie te verbeteren.
"""
import sys
import os

# Voeg src directory toe aan Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf
from src.mcp_invoice_processor.processing.classification import classify_document, DocumentType

def debug_amazon_invoice():
    """Debug Amazon factuur classificatie."""
    print("=== Amazon Factuur Debug ===")
    
    pdf_file = "amazon_rugtas-factuur.pdf"
    
    if not os.path.exists(pdf_file):
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
        
        # Test classificatie
        doc_type = classify_document(text)
        print(f"Gedetecteerd type: {doc_type}")
        
        # Analyseer trefwoorden
        text_lower = text.lower()
        
        # CV trefwoorden
        cv_keywords = {
            "ervaring", "opleiding", "vaardigheden", "curriculum vitae", "werkervaring",
            "education", "experience", "skills", "competenties", "diploma",
            "werkgever", "employer", "functie", "position", "carrière", "career"
        }
        
        # Factuur trefwoorden
        invoice_keywords = {
            "factuur", "invoice", "totaal", "total", "bedrag", "amount", "btw", "vat",
            "klant", "customer", "leverancier", "supplier", "artikel", "item",
            "prijs", "price", "kosten", "costs", "betaling", "payment"
        }
        
        # Tel trefwoorden
        cv_score = sum(1 for keyword in cv_keywords if keyword in text_lower)
        invoice_score = sum(1 for keyword in invoice_keywords if keyword in text_lower)
        
        print(f"CV score: {cv_score}")
        print(f"Factuur score: {invoice_score}")
        
        # Toon gevonden trefwoorden
        found_cv = [kw for kw in cv_keywords if kw in text_lower]
        found_invoice = [kw for kw in invoice_keywords if kw in text_lower]
        
        print(f"Gevonden CV trefwoorden: {found_cv}")
        print(f"Gevonden factuur trefwoorden: {found_invoice}")
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_amazon_invoice()
