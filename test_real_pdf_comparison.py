#!/usr/bin/env python3
"""
Uitgebreide test met echte PDF factuur (Amazon) + synthetische data.
Vergelijkt alle extractie methodes op zowel tekst als PDF input.
"""

import asyncio
import logging
import sys
import os
import json
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_invoice_processor.processing import ExtractionMethod, extract_structured_data
from mcp_invoice_processor.processing.classification import classify_document
from mcp_invoice_processor.processing.pipeline import process_document_pdf, process_document_text
from mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
SYNTHETIC_INVOICE = """
FACTUUR

Factuurnummer: INV-2024-001
Factuurdatum: 15 maart 2024
Vervaldatum: 15 april 2024

Van:
TechCorp B.V.
Techstraat 123
1234 AB Amsterdam
BTW: NL123456789B01

Aan:
ClientCorp B.V.
Clientlaan 456
5678 CD Rotterdam
BTW: NL987654321B01

Omschrijving                    Aantal  Prijs    Totaal
Softwarelicentie                    1   €500,00  €500,00
Consultancy uren                   10   €75,00   €750,00
Support contract                    1   €200,00  €200,00

Subtotaal:                                      €1.450,00
BTW (21%):                                       €304,50
Totaal:                                        €1.754,50

Betalingsvoorwaarden: 30 dagen
Betalingsmethode: Bankoverschrijving
Referentie: PROJECT-2024-A

Opmerkingen: Bedankt voor uw opdracht! Volgende levering in april.
"""

PDF_FILE_PATH = "amazon_rugtas-factuur.pdf"

def calculate_detailed_completeness(data: Dict[str, Any]) -> Dict[str, float]:
    """Bereken gedetailleerde completeness scores."""
    if not data:
        return {"overall": 0.0, "basic": 0.0, "financial": 0.0, "items": 0.0}
    
    # Basic fields
    basic_fields = ['invoice_number', 'invoice_date', 'supplier_name', 'customer_name']
    basic_filled = sum(1 for field in basic_fields if data.get(field) and data[field] != "")
    basic_score = (basic_filled / len(basic_fields)) * 100
    
    # Financial fields
    financial_fields = ['subtotal', 'vat_amount', 'total_amount']
    financial_filled = sum(1 for field in financial_fields if data.get(field) and data[field] != 0)
    financial_score = (financial_filled / len(financial_fields)) * 100
    
    # Line items
    line_items = data.get('line_items', [])
    items_score = 100.0 if isinstance(line_items, list) and len(line_items) > 0 else 0.0
    
    # Overall score
    all_important_fields = basic_fields + financial_fields + ['line_items']
    overall_filled = basic_filled + financial_filled + (1 if len(line_items) > 0 else 0)
    overall_score = (overall_filled / len(all_important_fields)) * 100
    
    return {
        "overall": overall_score,
        "basic": basic_score, 
        "financial": financial_score,
        "items": items_score
    }

def print_detailed_result(result: Dict[str, Any], method_name: str, source: str):
    """Print gedetailleerd resultaat met alle metrics."""
    
    if not result:
        print(f"\n❌ {method_name} ({source}): Geen resultaat")
        return
    
    scores = calculate_detailed_completeness(result)
    
    print(f"\n✅ {method_name} ({source}):")
    print(f"   📊 Scores: Overall {scores['overall']:.1f}% | Basic {scores['basic']:.1f}% | Financial {scores['financial']:.1f}% | Items {scores['items']:.1f}%")
    print(f"   📋 Invoice: {result.get('invoice_number', 'N/A')} (ID: {result.get('invoice_id', 'N/A')})")
    print(f"   📅 Datum: {result.get('invoice_date', 'N/A')} → {result.get('due_date', 'N/A')}")
    print(f"   🏢 Van: {result.get('supplier_name', 'N/A')}")
    print(f"   👥 Aan: {result.get('customer_name', 'N/A')}")
    print(f"   💰 Financieel: €{result.get('subtotal', 'N/A')} + €{result.get('vat_amount', 'N/A')} = €{result.get('total_amount', 'N/A')}")
    
    line_items = result.get('line_items', [])
    print(f"   📦 Line items: {len(line_items)}")
    for i, item in enumerate(line_items[:3]):  # Toon max 3 items
        if isinstance(item, dict):
            desc = item.get('description', 'N/A')
            qty = item.get('quantity', 'N/A')
            price = item.get('unit_price', 'N/A')
            total = item.get('line_total', 'N/A')
            print(f"     [{i+1}] {desc}: {qty} × €{price} = €{total}")
    
    if len(line_items) > 3:
        print(f"     ... en {len(line_items) - 3} meer")

async def test_method_on_source(text: str, source_name: str, method: ExtractionMethod, method_name: str) -> Dict[str, Any]:
    """Test een specifieke methode op een data source."""
    
    try:
        doc_type = classify_document(text)
        result = await extract_structured_data(text, doc_type, None, method)
        
        if result:
            result_dict = result.model_dump()
            print_detailed_result(result_dict, method_name, source_name)
            return result_dict
        else:
            logger.error(f"❌ {method_name} op {source_name} gaf None terug!")
            return {}
            
    except Exception as e:
        logger.error(f"❌ {method_name} op {source_name} fout: {e}")
        return {}

async def comprehensive_pdf_test():
    """Uitgebreide test met zowel synthetische als echte PDF data."""
    
    logger.info("🚀 Starten uitgebreide PDF + tekst vergelijking...")
    
    # Check of PDF bestaat
    if not os.path.exists(PDF_FILE_PATH):
        logger.error(f"❌ PDF bestand niet gevonden: {PDF_FILE_PATH}")
        return
    
    # Extraheer tekst uit PDF
    logger.info("📄 Extractie tekst uit Amazon PDF...")
    try:
        with open(PDF_FILE_PATH, 'rb') as f:
            pdf_bytes = f.read()
        pdf_text = extract_text_from_pdf(pdf_bytes)
        
        if not pdf_text or len(pdf_text.strip()) < 50:
            logger.error("❌ Onvoldoende tekst geëxtraheerd uit PDF")
            return
            
        logger.info(f"✅ PDF tekst geëxtraheerd: {len(pdf_text)} karakters")
        logger.info(f"📋 Preview: {pdf_text[:200]}...")
        
    except Exception as e:
        logger.error(f"❌ PDF extractie fout: {e}")
        return
    
    # Test configuratie
    methods = [
        (ExtractionMethod.JSON_SCHEMA, "JSON Schema"),
        (ExtractionMethod.PROMPT_PARSING, "Prompt Parsing"), 
        (ExtractionMethod.HYBRID, "🔥 HYBRID")
    ]
    
    sources = [
        (SYNTHETIC_INVOICE, "Synthetisch"),
        (pdf_text, "Amazon PDF")
    ]
    
    # Resultaten opslag
    all_results = {}
    
    # Test alle combinaties
    print(f"\n" + "="*80)
    print(f"🧪 TESTING ALLE METHODES OP ALLE BRONNEN")
    print(f"="*80)
    
    for source_text, source_name in sources:
        print(f"\n📊 BRON: {source_name}")
        print(f"-" * 40)
        
        source_results = {}
        
        for method, method_name in methods:
            logger.info(f"🔬 Testing {method_name} op {source_name}...")
            result = await test_method_on_source(source_text, source_name, method, method_name)
            source_results[method.value] = result
        
        all_results[source_name] = source_results
    
    # Vergelijkingsanalyse
    print(f"\n" + "="*80)
    print(f"📈 VERGELIJKINGSANALYSE")
    print(f"="*80)
    
    # Per methode vergelijking
    for method, method_name in methods:
        print(f"\n🔍 {method_name} VERGELIJKING:")
        print(f"-" * 40)
        
        for source_name in ["Synthetisch", "Amazon PDF"]:
            result = all_results[source_name].get(method.value, {})
            if result:
                scores = calculate_detailed_completeness(result)
                print(f"  {source_name:12}: {scores['overall']:5.1f}% | Items: {len(result.get('line_items', []))}")
            else:
                print(f"  {source_name:12}: ❌ FAILED")
    
    # Per bron vergelijking  
    print(f"\n🏆 BESTE METHODE PER BRON:")
    print(f"-" * 40)
    
    for source_name in ["Synthetisch", "Amazon PDF"]:
        best_method = None
        best_score = 0
        
        for method, method_name in methods:
            result = all_results[source_name].get(method.value, {})
            if result:
                score = calculate_detailed_completeness(result)["overall"]
                if score > best_score:
                    best_score = score
                    best_method = method_name
        
        if best_method:
            print(f"  {source_name:12}: {best_method} ({best_score:.1f}%)")
        else:
            print(f"  {source_name:12}: ❌ Alle methodes gefaald")
    
    # Overall winnaar
    print(f"\n🎉 OVERALL ANALYSE:")
    print(f"-" * 40)
    
    method_totals = {}
    for method, method_name in methods:
        total_score = 0
        success_count = 0
        
        for source_name in ["Synthetisch", "Amazon PDF"]:
            result = all_results[source_name].get(method.value, {})
            if result:
                score = calculate_detailed_completeness(result)["overall"]
                total_score += score
                success_count += 1
        
        avg_score = total_score / max(success_count, 1)
        method_totals[method_name] = (avg_score, success_count)
        print(f"  {method_name:15}: Avg {avg_score:5.1f}% ({success_count}/2 bronnen succesvol)")
    
    # Bepaal overall winnaar
    best_overall = max(method_totals.items(), key=lambda x: (x[1][1], x[1][0]))
    print(f"\n🏆 OVERALL WINNAAR: {best_overall[0]} (Avg {best_overall[1][0]:.1f}%, {best_overall[1][1]}/2 succesvol)")
    
    return all_results

if __name__ == "__main__":
    results = asyncio.run(comprehensive_pdf_test())
