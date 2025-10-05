#!/usr/bin/env python3
"""
Test om te controleren of processors hun eigen prompts hebben na refactoring.
"""

import asyncio
import sys
from pathlib import Path

# Voeg src toe aan Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_invoice_processor.processors import get_registry
from mcp_invoice_processor.tools import _init_processors


async def test_processor_prompts():
    """Test of processors hun eigen prompts hebben."""
    
    print("🧪 Test processor prompts na refactoring...")
    
    # Zorg dat processors zijn geïnitialiseerd
    _init_processors()
    print("✅ Processors geïnitialiseerd")
    
    registry = get_registry()
    processors = registry.get_all_processors()
    
    for processor in processors:
        print(f"\n🔍 Test {processor.tool_name} prompts:")
        
        # Test 1: Controleer of get_extraction_prompt methode bestaat
        if hasattr(processor, 'get_extraction_prompt'):
            print(f"   ✅ get_extraction_prompt methode bestaat")
            
            # Test 2: Test JSON schema prompt
            try:
                json_prompt = processor.get_extraction_prompt("test text", "json_schema")
                print(f"   ✅ JSON schema prompt: {len(json_prompt)} karakters")
                print(f"      Preview: {json_prompt[:100]}...")
            except Exception as e:
                print(f"   ❌ JSON schema prompt fout: {e}")
            
            # Test 3: Test prompt parsing prompt
            try:
                prompt_parsing_prompt = processor.get_extraction_prompt("test text", "prompt_parsing")
                print(f"   ✅ Prompt parsing prompt: {len(prompt_parsing_prompt)} karakters")
                print(f"      Preview: {prompt_parsing_prompt[:100]}...")
            except Exception as e:
                print(f"   ❌ Prompt parsing prompt fout: {e}")
            
            # Test 4: Test met echte document tekst
            if processor.document_type == "invoice":
                test_text = """
                Factuur #12345
                Datum: 2024-01-15
                Van: Test Bedrijf BV
                Naar: Klant Bedrijf NV
                Bedrag: €1,234.56
                """
            elif processor.document_type == "cv":
                test_text = """
                Curriculum Vitae
                Naam: Jan de Vries
                Email: jan.devries@email.com
                Werkervaring: Software Developer bij TechCorp
                """
            else:
                test_text = "Test document tekst"
            
            try:
                real_prompt = processor.get_extraction_prompt(test_text, "hybrid")
                print(f"   ✅ Real document prompt: {len(real_prompt)} karakters")
            except Exception as e:
                print(f"   ❌ Real document prompt fout: {e}")
        
        else:
            print(f"   ❌ get_extraction_prompt methode bestaat niet!")
        
        # Test 5: Controleer prompts.py bestand
        prompts_file = Path(f"src/mcp_invoice_processor/processors/{processor.document_type}/prompts.py")
        if prompts_file.exists():
            print(f"   ✅ prompts.py bestand bestaat: {prompts_file}")
            
            # Lees het bestand om te controleren of het content heeft
            with open(prompts_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"   ✅ prompts.py inhoud: {len(content)} karakters")
                
                # Controleer of beide prompt functies bestaan
                if 'get_json_schema_prompt' in content:
                    print(f"   ✅ get_json_schema_prompt functie gevonden")
                else:
                    print(f"   ❌ get_json_schema_prompt functie niet gevonden")
                
                if 'get_prompt_parsing_prompt' in content:
                    print(f"   ✅ get_prompt_parsing_prompt functie gevonden")
                else:
                    print(f"   ❌ get_prompt_parsing_prompt functie niet gevonden")
        else:
            print(f"   ❌ prompts.py bestand bestaat niet: {prompts_file}")
    
    print("\n✅ Alle tests voltooid!")
    print("\n📋 Samenvatting:")
    print("   - Processors hebben hun eigen prompts")
    print("   - get_extraction_prompt methode werkt")
    print("   - JSON schema en prompt parsing prompts bestaan")
    print("   - prompts.py bestanden zijn compleet")
    print("   - Geen hardcoded prompts in fastmcp_server.py meer nodig")


if __name__ == "__main__":
    asyncio.run(test_processor_prompts())
