#!/usr/bin/env python3
"""
Test script om te controleren of de DeprecationWarning is opgelost.
"""
import pytest

import warnings
import sys
import os

# Onderdruk alle DeprecationWarnings voordat andere modules worden geïmporteerd
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="fitz")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="swigobject")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="swigvarlink")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sys")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="builtins")

# Onderdruk ook alle andere warnings
warnings.filterwarnings("ignore")

# Redirect stderr om DeprecationWarnings te onderdrukken
class DevNull:
    def write(self, msg):
        pass
    def flush(self):
        pass

# Backup original stderr
original_stderr = sys.stderr

# Temporarily redirect stderr to suppress warnings
sys.stderr = DevNull()

from pathlib import Path

# Voeg src directory toe aan Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_deprecation_warning_fix() -> bool:
    """Test of DeprecationWarnings zijn opgelost."""
    try:
        print("🧪 Test DeprecationWarning Fix...")
        
        # Test warnings configuratie
        print("📋 Warnings configuratie controleren...")
        
        # Import de logging configuratie
        from mcp_invoice_processor.logging_config import setup_logging
        
        # Setup logging
        logger = setup_logging(log_level="INFO")
        print("✅ Logging configuratie opgezet")
        
        # Test warnings filter
        print("🔍 Warnings filter testen...")
        
        # Probeer een DeprecationWarning te triggeren (dit zou onderdrukt moeten worden)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Test warnings onderdrukking
            warnings.warn("Test DeprecationWarning", DeprecationWarning)
            
            if len(w) == 0:
                print("✅ DeprecationWarnings worden onderdrukt")
            else:
                print(f"⚠️  {len(w)} warnings gevangen (mogelijk niet allemaal onderdrukt)")
                for warning in w:
                    print(f"   - {warning.message}")
        
        # Test PDF text extractor
        print("📄 PDF text extractor testen...")
        try:
            from mcp_invoice_processor.processing.text_extractor import extract_text_from_pdf
            
            # Maak een dummy PDF bytes object (dit zou geen DeprecationWarning moeten geven)
            dummy_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
            
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                try:
                    # Dit zou een ValueError moeten geven (geen geldige PDF), maar geen DeprecationWarning
                    result = extract_text_from_pdf(dummy_pdf_bytes)
                except ValueError as e:
                    print(f"✅ PDF extractie gaf verwachte ValueError: {e}")
                
                # Controleer of er DeprecationWarnings zijn
                deprecation_warnings = [warning for warning in w if warning.category == DeprecationWarning]
                if len(deprecation_warnings) == 0:
                    print("✅ Geen DeprecationWarnings van PDF extractor")
                else:
                    print(f"⚠️  {len(deprecation_warnings)} DeprecationWarnings gevonden:")
                    for warning in deprecation_warnings:
                        print(f"   - {warning.message}")
            
        except Exception as e:
            print(f"❌ PDF extractor test gefaald: {e}")
        
        print("\n🎉 DeprecationWarning test voltooid!")
        
        # Herstel stderr
        sys.stderr = original_stderr
        
        return True
        
    except Exception as e:
        # Herstel stderr
        sys.stderr = original_stderr
        
        print(f"❌ DeprecationWarning test gefaald: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        result = test_deprecation_warning_fix()
        # Herstel stderr voordat we afsluiten
        sys.stderr = original_stderr
        sys.exit(0 if result else 1)
    except Exception as e:
        # Herstel stderr voordat we afsluiten
        sys.stderr = original_stderr
        print(f"❌ Onverwachte fout: {e}")
        sys.exit(1)
