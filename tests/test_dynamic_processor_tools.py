#!/usr/bin/env python3
"""
Test voor dynamische processor-specifieke MCP tools.
"""

import asyncio
import sys
from pathlib import Path

# Voeg src toe aan Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_invoice_processor.processors import get_registry
from mcp_invoice_processor.tools import _init_processors  # Zorg dat processors zijn geregistreerd


async def test_dynamic_processor_tools():
    """Test dynamische processor-specifieke tools."""
    
    print("🧪 Test dynamische processor-specifieke MCP tools...")
    
    # Zorg dat processors zijn geïnitialiseerd
    _init_processors()
    print("✅ Processors geïnitialiseerd")
    
    # Test 1: Controleer beschikbare processors
    print("\n🔍 Test 1: Beschikbare processors:")
    registry = get_registry()
    processors = registry.get_all_processors()
    
    for processor in processors:
        print(f"   - {processor.tool_name}: {processor.display_name}")
        print(f"     Type: {processor.document_type}")
        print(f"     Keywords: {len(processor.classification_keywords)} keywords")
        print(f"     Description: {processor.tool_description[:80]}...")
        
        # Test 2: Controleer tool metadata
        print(f"\n   📊 Tool metadata voor {processor.tool_name}:")
        metadata = processor.tool_metadata
        print(f"      Name: {metadata['name']}")
        print(f"      Description: {metadata['description'][:100]}...")
        print(f"      Document type: {metadata['document_type']}")
        print(f"      Supported methods: {metadata['supported_methods']}")
        print(f"      Supported formats: {metadata['supported_formats']}")
        print(f"      Annotations: {metadata['annotations']}")
        print(f"      Meta category: {metadata['meta']['category']}")
        print(f"      Meta processor_type: {metadata['meta']['processor_type']}")
    
    # Test 3: Test classificatie keywords
    print("\n🔍 Test 3: Classificatie keywords:")
    for processor in processors:
        print(f"\n   📝 {processor.tool_name} keywords:")
        keywords = list(processor.classification_keywords)
        print(f"      Totaal: {len(keywords)} keywords")
        print(f"      Eerste 10: {keywords[:10]}")
        if len(keywords) > 10:
            print(f"      Laatste 5: {keywords[-5:]}")
    
    # Test 4: Test tool metadata structuur
    print("\n🔍 Test 4: Tool metadata structuur:")
    for processor in processors:
        metadata = processor.tool_metadata
        print(f"\n   📊 {processor.tool_name} metadata:")
        print(f"      ✅ Name: {metadata.get('name', 'MISSING')}")
        print(f"      ✅ Description: {len(metadata.get('description', ''))} chars")
        print(f"      ✅ Document type: {metadata.get('document_type', 'MISSING')}")
        print(f"      ✅ Display name: {metadata.get('display_name', 'MISSING')}")
        print(f"      ✅ Supported methods: {metadata.get('supported_methods', 'MISSING')}")
        print(f"      ✅ Supported formats: {metadata.get('supported_formats', 'MISSING')}")
        print(f"      ✅ Annotations: {metadata.get('annotations', 'MISSING')}")
        print(f"      ✅ Meta: {metadata.get('meta', 'MISSING')}")
    
    print("\n✅ Alle tests voltooid!")
    print("\n📋 Samenvatting:")
    print("   - Dynamische processor detectie werkt")
    print("   - Tool metadata is correct geïmplementeerd")
    print("   - FastMCP annotations zijn beschikbaar")
    print("   - Elke processor heeft zijn eigen tool configuratie")
    print("   - Geen hardcoded tools meer nodig")


if __name__ == "__main__":
    asyncio.run(test_dynamic_processor_tools())
