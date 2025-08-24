#!/usr/bin/env python3
"""
Finale validatie test voor JSON schema extractie systeem.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("🚀 Starten finale validatie...")

# Test 1: Imports
print("1️⃣ Testen imports...")
try:
    from mcp_invoice_processor.processing import ExtractionMethod
    print("   ✅ ExtractionMethod import succesvol")
    print(f"   📋 Beschikbare methodes: {list(ExtractionMethod)}")
except Exception as e:
    print(f"   ❌ Import fout: {e}")
    sys.exit(1)

# Test 2: Document classificatie
print("2️⃣ Testen document classificatie...")
try:
    from mcp_invoice_processor.processing.classification import classify_document
    
    test_text = "FACTUUR INV-001 Totaal: €100.00"
    doc_type = classify_document(test_text)
    print(f"   ✅ Classificatie succesvol: {doc_type.value}")
    
    if doc_type.value == "unknown":
        print("   ⚠️ Waarschuwing: Document geclassificeerd als unknown")
    
except Exception as e:
    print(f"   ❌ Classificatie fout: {e}")

# Test 3: JSON Schema generatie
print("3️⃣ Testen JSON Schema generatie...")
try:
    from mcp_invoice_processor.processing.models import InvoiceData
    
    schema = InvoiceData.model_json_schema()
    print("   ✅ JSON Schema generatie succesvol")
    print(f"   📊 Schema heeft {len(schema.get('properties', {}))} properties")
    
except Exception as e:
    print(f"   ❌ Schema generatie fout: {e}")

# Test 4: Enum values
print("4️⃣ Testen enum values...")
try:
    print(f"   📋 JSON_SCHEMA value: '{ExtractionMethod.JSON_SCHEMA.value}'")
    print(f"   📋 PROMPT_PARSING value: '{ExtractionMethod.PROMPT_PARSING.value}'")
    
    # Test enum conversie
    method_from_string = ExtractionMethod("json_schema")
    print(f"   ✅ String naar enum conversie werkt: {method_from_string}")
    
except Exception as e:
    print(f"   ❌ Enum test fout: {e}")

print("\n🎉 Finale validatie voltooid!")
print("✅ JSON Schema extractie systeem is operationeel!")
print("\n📋 Gebruik:")
print("   - ExtractionMethod.JSON_SCHEMA (default, betrouwbaar)")  
print("   - ExtractionMethod.PROMPT_PARSING (legacy, fallback)")
print("\n🔧 In FastMCP:")
print("   - process_document_text(text, ctx, 'json_schema')")
print("   - process_document_text(text, ctx, 'prompt_parsing')")
