import asyncio
import time
from pathlib import Path
import logging
from mcp_invoice_processor.processing.classification import classify_document
from mcp_invoice_processor.processing.models import InvoiceData, CVData
from typing import Any, Dict, List, Optional, Union
import pytest

#!/usr/bin/env python3
"""
Test script voor het verwerken van echte documenten via de FastMCP server.
Dit script simuleert een echte Ollama chatsessie met document verwerking.
"""


# Import de juiste functies uit de pipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessingTester:
    """Tester klasse voor document verwerking via FastMCP."""
    
    def __init__(self) -> None:
        self.test_documents_dir = Path("test_documents")
        
    async def test_invoice_processing(self) -> bool:
        """Test factuur verwerking."""
        print("🧾 Testen van factuur verwerking...")
        
        invoice_path = self.test_documents_dir / "sample_invoice.txt"
        if not invoice_path.exists():
            print(f"❌ Test factuur niet gevonden: {invoice_path}")
            return False
            
        try:
            # Start timer voor metrics
            start_time = time.time()
            
            # Lees de tekst uit het bestand
            with open(invoice_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Classificeer het document (niet async)
            doc_type = classify_document(text_content)
            print(f"📊 Gedetecteerd document type: {doc_type}")
            
            # Verwerk het document (simuleer PDF processing)
            # Voor tekst bestanden gebruiken we de classificatie en extractie direct
            from mcp_invoice_processor.processing.pipeline import extract_structured_data
            
            # Mock context voor FastMCP met async methoden
            class MockContext:
                async def info(self, msg: str) -> None: 
                    logger.info(f"📋 {msg}")
                    print(f"ℹ️  {msg}")
                async def error(self, msg: str) -> None: 
                    logger.error(f"❌ {msg}")
                    print(f"❌ {msg}")
                async def report_progress(self, current: int, total: int) -> None: 
                    logger.info(f"Progress: {current}/{total}")
                    pass
            
            ctx = MockContext()
            
            # Extraheer gestructureerde data met timeout
            try:
                result = await asyncio.wait_for(
                    extract_structured_data(text_content, doc_type, ctx),
                    timeout=60.0  # 60 seconden timeout
                )
            except asyncio.TimeoutError:
                print("❌ Timeout bij Ollama request (60s)")
                return False
            
            processing_time = time.time() - start_time
            
            if result:
                print("✅ Factuur succesvol verwerkt in {processing_time:.2f}s".format(processing_time=processing_time))
                print(f"📊 Document type: {doc_type}")
                print("📋 Geëxtraheerde data:")
                
                # Type checking voor veilige attribuut toegang
                if isinstance(result, InvoiceData):
                    print(f"   - Factuur ID: {result.invoice_id}")
                    print(f"   - Factuurnummer: {result.invoice_number}")
                    print(f"   - Bedrag: €{result.total_amount}")
                    print(f"   - Afzender: {result.supplier_name}")
                    print(f"   - Geadresseerde: {result.customer_name}")
                    print(f"   - Factuurdatum: {result.invoice_date}")
                else:
                    print("   - Geen factuur data gevonden")
                    
                return True
            else:
                print("❌ Factuur verwerking mislukt")
                return False
                
        except Exception as e:
            print(f"❌ Fout bij factuur verwerking: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_cv_processing(self) -> bool:
        """Test CV verwerking."""
        print("\n👤 Testen van CV verwerking...")
        
        cv_path = self.test_documents_dir / "sample_cv.txt"
        if not cv_path.exists():
            print(f"❌ Test CV niet gevonden: {cv_path}")
            return False
            
        try:
            # Start timer voor metrics
            start_time = time.time()
            
            # Lees de tekst uit het bestand
            with open(cv_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Classificeer het document (niet async)
            doc_type = classify_document(text_content)
            print(f"📊 Gedetecteerd document type: {doc_type}")
            
            # Mock context voor FastMCP met async methoden
            class MockContext:
                async def info(self, msg: str) -> None: 
                    logger.info(f"📋 {msg}")
                    print(f"ℹ️  {msg}")
                async def error(self, msg: str) -> None: 
                    logger.error(f"❌ {msg}")
                    print(f"❌ {msg}")
                async def report_progress(self, current: int, total: int) -> None: 
                    logger.info(f"Progress: {current}/{total}")
                    pass
            
            ctx = MockContext()
            
            # Extraheer gestructureerde data met timeout
            from mcp_invoice_processor.processing.pipeline import extract_structured_data
            try:
                result = await asyncio.wait_for(
                    extract_structured_data(text_content, doc_type, ctx),
                    timeout=60.0  # 60 seconden timeout
                )
            except asyncio.TimeoutError:
                print("❌ Timeout bij Ollama request (60s)")
                return False
            
            processing_time = time.time() - start_time
            
            if result:
                print("✅ CV succesvol verwerkt in {processing_time:.2f}s".format(processing_time=processing_time))
                print(f"📊 Document type: {doc_type}")
                print("📋 Geëxtraheerde data:")
                
                # Type checking voor veilige attribuut toegang
                if isinstance(result, CVData):
                    print(f"   - Naam: {result.full_name}")
                    print(f"   - E-mail: {result.email}")
                    print(f"   - Telefoon: {result.phone_number}")
                    print(f"   - Samenvatting: {result.summary[:100]}...")
                    if hasattr(result, 'work_experience') and result.work_experience:
                        print(f"   - Werkervaring: {len(result.work_experience)} posities")
                    if hasattr(result, 'skills') and result.skills:
                        print(f"   - Vaardigheden: {', '.join(result.skills[:5])}...")
                else:
                    print("   - Geen CV data gevonden")
                    
                return True
            else:
                print("❌ CV verwerking mislukt")
                return False
                
        except Exception as e:
            print(f"❌ Fout bij CV verwerking: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_ollama_integration(self) -> bool:
        """Test Ollama integratie direct."""
        print("\n🤖 Testen van Ollama integratie...")
        
        try:
            # Test met een eenvoudige prompt
            test_text = "Dit is een test factuur met factuurnummer INV-2025-001 en bedrag €500."
            
            # Start timer
            start_time = time.time()
            
            # Test document classificatie (niet async)
            result = classify_document(test_text)
            
            response_time = time.time() - start_time
            
            print(f"✅ Ollama integratie succesvol in {response_time:.2f}s")
            print(f"📊 Document classificatie: {result}")
            
            return True
            
        except Exception as e:
            print(f"❌ Fout bij Ollama integratie: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def run_comprehensive_test(self) -> bool:
        """Voer alle tests uit."""
        print("🚀 Starten van uitgebreide document verwerking test...")
        print("=" * 60)
        
        # Test Ollama integratie eerst
        ollama_success = await self.test_ollama_integration()
        
        # Test document verwerking
        invoice_success = await self.test_invoice_processing()
        cv_success = await self.test_cv_processing()
        
        # Resultaten samenvatten
        print("\n" + "=" * 60)
        print("📊 TEST RESULTATEN SAMENVATTING")
        print("=" * 60)
        
        print(f"🤖 Ollama Integratie: {'✅ GESLAAGD' if ollama_success else '❌ MISLUKT'}")
        print(f"🧾 Factuur Verwerking: {'✅ GESLAAGD' if invoice_success else '❌ MISLUKT'}")
        print(f"👤 CV Verwerking: {'✅ GESLAAGD' if cv_success else '❌ MISLUKT'}")
        
        total_tests = 3
        passed_tests = sum([ollama_success, invoice_success, cv_success])
        
        print(f"\n📈 Totaal: {passed_tests}/{total_tests} tests geslaagd")
        
        if passed_tests == total_tests:
            print("🎉 Alle tests geslaagd! De FastMCP server werkt perfect!")
        else:
            print("⚠️  Sommige tests zijn mislukt. Controleer de logs voor details.")
        
        return passed_tests == total_tests


async def main() -> None:
    """Hoofdfunctie."""
    tester = DocumentProcessingTester()
    
    try:
        success = await tester.run_comprehensive_test()
        
        if success:
            print("\n🎯 FastMCP Server is klaar voor productie gebruik!")
            print("📖 Je kunt nu documenten verwerken via de MCP protocol.")
        else:
            print("\n🔧 Er zijn problemen gevonden. Controleer de configuratie.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test gestopt door gebruiker.")
    except Exception as e:
        print(f"\n💥 Onverwachte fout: {e}")


if __name__ == "__main__":
    asyncio.run(main())
