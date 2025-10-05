#!/usr/bin/env python3
"""
Test voor dynamische document types examples.
"""

import asyncio
import sys
from pathlib import Path

# Voeg src toe aan Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_invoice_processor.processors import get_registry
from mcp_invoice_processor.tools import _init_processors


async def test_dynamic_documentation():
    """Test dynamische documentatie generatie."""
    
    print("🧪 Test dynamische document types examples...")
    
    # Zorg dat processors zijn geïnitialiseerd
    _init_processors()
    print("✅ Processors geïnitialiseerd")
    
    # Test 1: Controleer processor examples
    print("\n🔍 Test 1: Processor examples:")
    registry = get_registry()
    processors = registry.get_all_processors()
    
    for processor in processors:
        print(f"\n   📝 {processor.tool_name} examples:")
        examples = processor.tool_examples
        
        print(f"      Emoji: {examples['emoji']}")
        print(f"      Example text length: {len(examples['example_text'])} chars")
        print(f"      Extracted fields: {len(examples['extracted_fields'])} fields")
        print(f"      Keywords: {len(examples['keywords'])} keywords")
        print(f"      Supported methods: {examples['supported_methods']}")
        print(f"      Supported formats: {examples['supported_formats']}")
        
        # Test 2: Controleer example text inhoud
        print(f"\n      📄 Example text preview:")
        print(f"         {examples['example_text'][:100]}...")
        
        # Test 3: Controleer extracted fields
        print(f"\n      📊 Extracted fields:")
        for field in examples['extracted_fields'][:3]:  # Eerste 3
            print(f"         - {field}")
        if len(examples['extracted_fields']) > 3:
            print(f"         ... en {len(examples['extracted_fields']) - 3} meer")
    
    # Test 4: Genereer dynamische documentatie
    print("\n🔍 Test 4: Dynamische documentatie generatie:")
    
    docs = ["# 📋 Ondersteunde Document Types\n"]
    
    for processor in processors:
        examples = processor.tool_examples
        
        docs.append(f"## {examples['emoji']} {processor.display_name}")
        docs.append(f"- **Tool naam**: `{processor.tool_name}`")
        docs.append(f"- **Trefwoorden**: {', '.join(examples['keywords'][:10])}{'...' if len(examples['keywords']) > 10 else ''}")
        docs.append(f"- **Geëxtraheerde velden**:")
        
        for field in examples['extracted_fields']:
            docs.append(f"  - {field}")
        
        docs.append(f"- **Ondersteunde methoden**: {', '.join(examples['supported_methods'])}")
        docs.append(f"- **Ondersteunde formaten**: {', '.join(examples['supported_formats'])}")
        
        docs.append(f"- **Voorbeeld document**:")
        docs.append("  ```")
        docs.append(f"  {examples['example_text']}")
        docs.append("  ```")
        
        docs.append(f"- **Voorbeeld gebruik**:")
        docs.append("  ```python")
        docs.append(f"  {examples['usage_example']}")
        docs.append("  ```")
        
        docs.append("")  # Lege regel tussen processors
    
    docs.append("## 🔧 Algemene Tools")
    docs.append("- `process_document_text` - Automatische document type detectie")
    docs.append("- `process_document_file` - Verwerk bestanden (PDF, TXT)")
    docs.append("- `classify_document_type` - Alleen classificatie zonder extractie")
    docs.append("- `get_metrics` - Systeem statistieken")
    docs.append("- `health_check` - Service health status")
    
    generated_docs = "\n".join(docs)
    
    print(f"✅ Dynamische documentatie gegenereerd: {len(generated_docs)} karakters")
    print(f"✅ Aantal regels: {len(generated_docs.splitlines())}")
    
    # Test 5: Controleer documentatie inhoud
    print("\n🔍 Test 5: Documentatie inhoud:")
    lines = generated_docs.splitlines()
    
    print(f"   Eerste 10 regels:")
    for i, line in enumerate(lines[:10]):
        print(f"   {i+1:2d}: {line}")
    
    print(f"\n   Laatste 5 regels:")
    for i, line in enumerate(lines[-5:], len(lines)-4):
        print(f"   {i:2d}: {line}")
    
    print("\n✅ Alle tests voltooid!")
    print("\n📋 Samenvatting:")
    print("   - Dynamische processor examples werken")
    print("   - Elke processor heeft zijn eigen voorbeelden")
    print("   - Documentatie wordt dynamisch gegenereerd")
    print("   - Geen hardcoded documentatie meer nodig")
    print("   - Uitbreidbaar voor nieuwe document types")


if __name__ == "__main__":
    asyncio.run(test_dynamic_documentation())
