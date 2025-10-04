#!/usr/bin/env python3
"""
Test voor de nieuwe hybrid extraction mode.
"""
import pytest

import asyncio
import logging
import sys
import os
import json
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mcp_invoice_processor.processing import ExtractionMethod, extract_structured_data
from mcp_invoice_processor.processing.classification import classify_document

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test invoice
TEST_INVOICE = """
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

def print_result_summary(result: Dict[str, Any], method_name: str):
    """Print een samenvatting van het extractie resultaat."""
    
    if not result:
        print(f"\n❌ {method_name}: Geen resultaat")
        return
    
    print(f"\n✅ {method_name} RESULTAAT:")
    print(f"   📋 Invoice: {result.get('invoice_number', 'N/A')} (ID: {result.get('invoice_id', 'N/A')})")
    print(f"   📅 Datum: {result.get('invoice_date', 'N/A')} → {result.get('due_date', 'N/A')}")
    print(f"   🏢 Van: {result.get('supplier_name', 'N/A')}")
    print(f"   👥 Aan: {result.get('customer_name', 'N/A')}")
    print(f"   💰 Totaal: €{result.get('total_amount', 'N/A')}")
    
    line_items = result.get('line_items', [])
    print(f"   📦 Line items: {len(line_items)}")
    for i, item in enumerate(line_items):
        if isinstance(item, dict):
            desc = item.get('description', 'N/A')
            qty = item.get('quantity', 'N/A')
            price = item.get('unit_price', 'N/A')
            total = item.get('line_total', 'N/A')
            print(f"     [{i+1}] {desc}: {qty} × €{price} = €{total}")

def calculate_simple_completeness(data: Dict[str, Any]) -> float:
    """Bereken eenvoudige completeness score."""
    if not data:
        return 0.0
    
    important_fields = [
        'invoice_number', 'invoice_date', 'supplier_name', 'customer_name',
        'total_amount', 'line_items'
    ]
    
    filled = 0
    for field in important_fields:
        value = data.get(field)
        if field == 'line_items':
            if isinstance(value, list) and len(value) > 0:
                filled += 1
        elif value is not None and value != "" and value != 0:
            filled += 1
    
    return (filled / len(important_fields)) * 100

async def test_all_methods():
    """Test alle extractie methodes en vergelijk resultaten."""
    
    logger.info("🚀 Testen alle extractie methodes...")
    
    # Classificeer document
    doc_type = classify_document(TEST_INVOICE)
    logger.info(f"📋 Document type: {doc_type.value}")
    
    results = {}
    methods = [
        (ExtractionMethod.JSON_SCHEMA, "JSON Schema"),
        (ExtractionMethod.PROMPT_PARSING, "Prompt Parsing"), 
        (ExtractionMethod.HYBRID, "🔥 HYBRID")
    ]
    
    for method, name in methods:
        logger.info(f"\n🔬 Testing {name} Mode...")
        
        try:
            result = await extract_structured_data(
                TEST_INVOICE, 
                doc_type, 
                None, 
                method
            )
            
            if result:
                result_dict = result.model_dump()
                results[method.value] = result_dict
                completeness = calculate_simple_completeness(result_dict)
                logger.info(f"✅ {name} succesvol! Completeness: {completeness:.1f}%")
                print_result_summary(result_dict, name)
            else:
                logger.error(f"❌ {name} gaf None terug!")
                results[method.value] = None
                
        except Exception as e:
            logger.error(f"❌ {name} fout: {e}")
            results[method.value] = None
    
    # Vergelijking
    print(f"\n🏆 FINALE VERGELIJKING:")
    print("=" * 60)
    
    for method, name in methods:
        result = results.get(method.value)
        if result:
            completeness = calculate_simple_completeness(result)
            line_items = len(result.get('line_items', []))
            print(f"{name:15}: {completeness:5.1f}% compleet, {line_items} line items")
        else:
            print(f"{name:15}: ❌ FAILED")
    
    # Bepaal winnaar
    best_method = None
    best_score = 0
    
    for method, name in methods:
        result = results.get(method.value)
        if result:
            score = calculate_simple_completeness(result)
            if score > best_score:
                best_score = score
                best_method = name
    
    if best_method:
        print(f"\n🎉 WINNAAR: {best_method} ({best_score:.1f}% compleet)")
    else:
        print(f"\n❌ Alle methodes gefaald!")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_all_methods())
