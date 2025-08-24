#!/usr/bin/env python3
"""
Test script om PDF verwerking direct te testen.
"""
import sys
import os
import asyncio

# Voeg src directory toe aan Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_pdf_processing():
    """Test PDF verwerking direct."""
    try:
        print("🧪 Test PDF Verwerking...")
        
        # Test PDF pad
        pdf_path = "amazon_rugtas-factuur.pdf"
        if not os.path.exists(pdf_path):
            print(f"❌ PDF bestand niet gevonden: {pdf_path}")
            return False
        
        print(f"✅ PDF bestand gevonden: {pdf_path}")
        
        # Import modules
        from src.mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf
        from src.mcp_invoice_processor.processing.classification import classify_document
        from src.mcp_invoice_processor.processing.pipeline import extract_structured_data
        from src.mcp_invoice_processor.processing.models import DocumentType
        
        print("✅ Modules geïmporteerd")
        
        # Stap 1: Tekst extractie
        print("\n📄 Stap 1: Tekst extractie...")
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        text = extract_text_from_pdf(pdf_bytes)
        print(f"✅ Tekst geëxtraheerd: {len(text)} karakters")
        print(f"   Eerste 200 karakters: {text[:200]}...")
        
        # Stap 2: Document classificatie
        print("\n🏷️  Stap 2: Document classificatie...")
        doc_type = classify_document(text)
        print(f"✅ Document geclassificeerd als: {doc_type.value}")
        
        # Stap 3: Gestructureerde data extractie
        print("\n🤖 Stap 3: Gestructureerde data extractie...")
        
        # Mock context voor logging
        class MockContext:
            async def info(self, msg):
                print(f"   INFO: {msg}")
            async def error(self, msg):
                print(f"   ERROR: {msg}")
        
        ctx = MockContext()
        
        # Test data extractie
        result = await extract_structured_data(text, doc_type, ctx)
        
        if result:
            print("✅ Gestructureerde data geëxtraheerd!")
            print(f"   Type: {type(result).__name__}")
            
            # Toon belangrijke velden
            if hasattr(result, 'invoice_id'):
                print(f"   Factuur ID: {result.invoice_id}")
            if hasattr(result, 'total_amount'):
                print(f"   Totaal bedrag: {result.total_amount}")
            if hasattr(result, 'supplier_name'):
                print(f"   Leverancier: {result.supplier_name}")
        else:
            print("❌ Geen gestructureerde data geëxtraheerd")
        
        print("\n🎉 PDF verwerking test voltooid!")
        return True
        
    except Exception as e:
        print(f"❌ PDF verwerking test gefaald: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main functie om async test uit te voeren."""
    try:
        # Maak nieuwe event loop voor de test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Voer async test uit
        success = loop.run_until_complete(test_pdf_processing())
        
        # Sluit loop
        loop.close()
        
        return success
        
    except Exception as e:
        print(f"❌ Test uitvoering gefaald: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
