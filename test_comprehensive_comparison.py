#!/usr/bin/env python3
"""
Uitgebreide vergelijking van JSON schema vs prompt parsing mode met alle nested velden.
"""

import asyncio
import logging
import sys
import os
import json
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_invoice_processor.processing import ExtractionMethod, extract_structured_data
from mcp_invoice_processor.processing.classification import classify_document
from mcp_invoice_processor.processing.models import InvoiceData, InvoiceLineItem

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Uitgebreide test invoice
DETAILED_INVOICE_TEXT = """
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

def print_nested_comparison(data1: Dict[str, Any], data2: Dict[str, Any], title1: str, title2: str):
    """Print een gedetailleerde vergelijking van twee data structuren."""
    
    print(f"\n📊 VERGELIJKING: {title1} vs {title2}")
    print("=" * 80)
    
    all_keys = set(data1.keys()) | set(data2.keys())
    
    for key in sorted(all_keys):
        val1 = data1.get(key, "❌ MISSING")
        val2 = data2.get(key, "❌ MISSING")
        
        # Bepaal status
        if val1 == val2:
            status = "✅ IDENTICAL"
        elif val1 == "❌ MISSING" or val2 == "❌ MISSING":
            status = "⚠️ MISSING"
        elif (val1 is None and val2 == "") or (val1 == "" and val2 is None):
            status = "🔄 EQUIVALENT"
        else:
            status = "❌ DIFFERENT"
        
        print(f"\n🔹 {key.upper()}: {status}")
        print(f"   {title1}: {val1}")
        print(f"   {title2}: {val2}")
        
        # Speciale behandeling voor line_items
        if key == "line_items" and isinstance(val1, list) and isinstance(val2, list):
            print(f"   📦 Line items count: {len(val1)} vs {len(val2)}")
            
            if len(val1) > 0 or len(val2) > 0:
                max_items = max(len(val1), len(val2))
                for i in range(max_items):
                    item1 = val1[i] if i < len(val1) else "❌ MISSING"
                    item2 = val2[i] if i < len(val2) else "❌ MISSING"
                    
                    print(f"   📋 Item {i+1}:")
                    if isinstance(item1, dict) and isinstance(item2, dict):
                        for item_key in set(item1.keys()) | set(item2.keys()):
                            item_val1 = item1.get(item_key, "❌ MISSING")
                            item_val2 = item2.get(item_key, "❌ MISSING")
                            item_status = "✅" if item_val1 == item_val2 else "❌"
                            print(f"     {item_status} {item_key}: {item_val1} | {item_val2}")
                    else:
                        print(f"     {title1}: {item1}")
                        print(f"     {title2}: {item2}")

def calculate_completeness_score(data: Dict[str, Any]) -> float:
    """Bereken completeness score (0-100)."""
    total_fields = 0
    filled_fields = 0
    
    for key, value in data.items():
        if key == "line_items":
            total_fields += 1
            if isinstance(value, list) and len(value) > 0:
                filled_fields += 1
                # Tel ook line item velden
                for item in value:
                    if isinstance(item, dict):
                        for item_key, item_value in item.items():
                            total_fields += 1
                            if item_value is not None and item_value != "" and item_value != 0:
                                filled_fields += 1
        else:
            total_fields += 1
            if value is not None and value != "" and value != 0:
                filled_fields += 1
    
    return (filled_fields / total_fields * 100) if total_fields > 0 else 0

async def comprehensive_comparison():
    """Uitgebreide vergelijking van beide extractie methodes."""
    
    logger.info("🚀 Starten uitgebreide vergelijking...")
    
    # Classificeer document
    doc_type = classify_document(DETAILED_INVOICE_TEXT)
    logger.info(f"📋 Document type: {doc_type.value}")
    
    results = {}
    
    # Test JSON Schema Mode
    logger.info("\n🔬 Testing JSON Schema Mode...")
    try:
        result_schema = await extract_structured_data(
            DETAILED_INVOICE_TEXT, 
            doc_type, 
            None, 
            ExtractionMethod.JSON_SCHEMA
        )
        
        if result_schema:
            results['json_schema'] = result_schema.model_dump()
            logger.info("✅ JSON Schema mode succesvol!")
        else:
            results['json_schema'] = {}
            logger.error("❌ JSON Schema mode gaf None terug!")
            
    except Exception as e:
        results['json_schema'] = {}
        logger.error(f"❌ JSON Schema mode fout: {e}")
    
    # Test Prompt Parsing Mode
    logger.info("\n🔬 Testing Prompt Parsing Mode...")
    try:
        result_parsing = await extract_structured_data(
            DETAILED_INVOICE_TEXT, 
            doc_type, 
            None, 
            ExtractionMethod.PROMPT_PARSING
        )
        
        if result_parsing:
            results['prompt_parsing'] = result_parsing.model_dump()
            logger.info("✅ Prompt Parsing mode succesvol!")
        else:
            results['prompt_parsing'] = {}
            logger.error("❌ Prompt Parsing mode gaf None terug!")
            
    except Exception as e:
        results['prompt_parsing'] = {}
        logger.error(f"❌ Prompt Parsing mode fout: {e}")
    
    # Vergelijking
    if results.get('json_schema') and results.get('prompt_parsing'):
        print_nested_comparison(
            results['json_schema'], 
            results['prompt_parsing'],
            "JSON Schema", 
            "Prompt Parsing"
        )
        
        # Completeness scores
        schema_score = calculate_completeness_score(results['json_schema'])
        parsing_score = calculate_completeness_score(results['prompt_parsing'])
        
        print(f"\n📈 COMPLETENESS SCORES:")
        print(f"   JSON Schema Mode: {schema_score:.1f}%")
        print(f"   Prompt Parsing Mode: {parsing_score:.1f}%")
        
        # Winner
        if schema_score > parsing_score:
            print(f"🏆 WINNER: JSON Schema Mode (+{schema_score-parsing_score:.1f}%)")
        elif parsing_score > schema_score:
            print(f"🏆 WINNER: Prompt Parsing Mode (+{parsing_score-schema_score:.1f}%)")
        else:
            print("🤝 TIE: Both methods equally complete")
            
    elif results.get('json_schema'):
        print(f"\n✅ Only JSON Schema Mode worked:")
        print(json.dumps(results['json_schema'], indent=2, ensure_ascii=False))
        
    elif results.get('prompt_parsing'):
        print(f"\n✅ Only Prompt Parsing Mode worked:")
        print(json.dumps(results['prompt_parsing'], indent=2, ensure_ascii=False))
        
    else:
        print("\n❌ Both methods failed!")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(comprehensive_comparison())
    print(f"\n🎉 Vergelijking voltooid!")
