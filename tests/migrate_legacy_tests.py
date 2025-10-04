"""
Automatische migratie script voor legacy tests naar v2.0 processors.

Dit script update automatisch oude imports naar nieuwe processor architecture.
"""

import re
from pathlib import Path
from typing import List, Tuple


# Import replacements
IMPORT_REPLACEMENTS = [
    # Classification
    (
        r'from mcp_invoice_processor\.processing\.classification import classify_document, DocumentType',
        'from mcp_invoice_processor.processors import get_registry'
    ),
    (
        r'from mcp_invoice_processor\.processing\.classification import classify_document',
        'from mcp_invoice_processor.processors import get_registry'
    ),
    (
        r'from mcp_invoice_processor\.processing\.classification import DocumentType',
        '# DocumentType is now string-based in processors'
    ),
    
    # Pipeline
    (
        r'from mcp_invoice_processor\.processing\.pipeline import extract_structured_data, ExtractionMethod',
        'from mcp_invoice_processor.processors import get_registry'
    ),
    (
        r'from mcp_invoice_processor\.processing\.pipeline import extract_structured_data',
        'from mcp_invoice_processor.processors import get_registry'
    ),
    (
        r'from mcp_invoice_processor\.processing\.pipeline import process_document_pdf, process_document_text',
        'from mcp_invoice_processor.processors import get_registry'
    ),
    
    # Merging
    (
        r'from mcp_invoice_processor\.processing\.merging import merge_partial_invoice_data, merge_partial_cv_data',
        '# Merging now via processor.merge_partial_results()'
    ),
    (
        r'from mcp_invoice_processor\.processing\.merging import merge_partial_invoice_data',
        '# Merging now via processor.merge_partial_results()'
    ),
    (
        r'from mcp_invoice_processor\.processing\.merging import merge_partial_cv_data',
        '# Merging now via processor.merge_partial_results()'
    ),
]

# Code replacements
CODE_REPLACEMENTS = [
    # Classification calls
    (
        r'doc_type = classify_document\((\w+)\)',
        r'registry = get_registry()\ndoc_type, confidence, processor = await registry.classify_document(\1, ctx)'
    ),
    (
        r'classify_document\((\w+)\)',
        r'(await get_registry().classify_document(\1, ctx))[0]'
    ),
    
    # DocumentType enum usage
    (
        r'DocumentType\.INVOICE',
        '"invoice"'
    ),
    (
        r'DocumentType\.CV',
        '"cv"'
    ),
    (
        r'DocumentType\.UNKNOWN',
        '"unknown"'
    ),
    (
        r'doc_type\.value',
        'doc_type'
    ),
    
    # Extract calls
    (
        r'await extract_structured_data\(([^,]+),\s*([^,]+),\s*([^,]+),?\s*([^)]*)\)',
        r'await processor.extract(\1, \3, method="\4" if "\4" else "hybrid")'
    ),
    
    # Merging calls
    (
        r'merge_partial_invoice_data\(([^)]+)\)',
        r'await processor.merge_partial_results(\1, ctx)'
    ),
    (
        r'merge_partial_cv_data\(([^)]+)\)',
        r'await processor.merge_partial_results(\1, ctx)'
    ),
]


def migrate_test_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Migreer een legacy test file naar v2.0 architecture.
    
    Returns:
        Tuple[bool, List[str]]: (success, messages)
    """
    messages = []
    
    try:
        # Lees file
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Apply import replacements
        for old_pattern, new_import in IMPORT_REPLACEMENTS:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_import, content)
                messages.append(f"  ✓ Updated import: {old_pattern[:50]}...")
        
        # Apply code replacements
        for old_pattern, new_code in CODE_REPLACEMENTS:
            matches = re.findall(old_pattern, content)
            if matches:
                content = re.sub(old_pattern, new_code, content)
                messages.append(f"  ✓ Updated code pattern: {old_pattern[:50]}...")
        
        # Check if anything changed
        if content != original_content:
            # Backup original
            backup_path = file_path.with_suffix('.py.bak')
            backup_path.write_text(original_content, encoding='utf-8')
            
            # Write updated content
            file_path.write_text(content, encoding='utf-8')
            
            messages.append(f"  ✅ File migrated (backup: {backup_path.name})")
            return True, messages
        else:
            messages.append(f"  ℹ️ No changes needed")
            return True, messages
            
    except Exception as e:
        messages.append(f"  ❌ Error: {e}")
        return False, messages


def main():
    """Main migration function."""
    print("🔄 Legacy Tests Migration Script v2.0")
    print("=" * 60)
    
    legacy_dir = Path("tests/legacy_tests")
    
    if not legacy_dir.exists():
        print("❌ Legacy tests directory niet gevonden")
        return
    
    # Find all test files
    test_files = list(legacy_dir.glob("test_*.py"))
    print(f"\n📁 Gevonden {len(test_files)} legacy test files\n")
    
    migrated = 0
    failed = 0
    
    for test_file in test_files:
        print(f"📝 Migreren: {test_file.name}")
        success, messages = migrate_test_file(test_file)
        
        for msg in messages:
            print(msg)
        
        if success:
            migrated += 1
        else:
            failed += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print(f"\n📊 Migratie Samenvatting:")
    print(f"   ✅ Succesvol: {migrated}")
    print(f"   ❌ Gefaald: {failed}")
    print(f"   📁 Totaal: {len(test_files)}")
    
    if failed == 0:
        print("\n🎉 Alle tests succesvol gemigreerd!")
        print("\n📋 Volgende stappen:")
        print("   1. Controleer de gemigreerde files in tests/legacy_tests/")
        print("   2. Run tests: uv run pytest tests/legacy_tests/")
        print("   3. Fix eventuele handmatige aanpassingen")
        print("   4. Verplaats werkende tests naar tests/")
    else:
        print(f"\n⚠️ {failed} test(s) gefaald. Check error messages hierboven.")


if __name__ == "__main__":
    main()

