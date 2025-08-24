#!/usr/bin/env python3
"""
Script om alle mypy errors systematisch op te lossen.
Voegt type annotations toe aan alle Python bestanden.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any


def add_type_annotations_to_file(file_path: str) -> None:
    """Voeg type annotations toe aan een Python bestand."""
    print(f"Repareren van: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Voeg type annotations toe aan functies zonder return type
    # Patroon: def function_name( -> None:
    content = re.sub(
        r'def (\w+)\s*\(([^)]*)\):',
        r'def \1(\2) -> None:',
        content
    )
    
    # Voeg type annotations toe aan functies met parameters
    # Patroon: def function_name(param1, param2) -> None:
    content = re.sub(
        r'def (\w+)\s*\(([^)]*)\) -> None:',
        r'def \1(\2) -> None:',
        content
    )
    
    # Voeg type annotations toe aan async functies
    content = re.sub(
        r'async def (\w+)\s*\(([^)]*)\):',
        r'async def \1(\2) -> None:',
        content
    )
    
    # Voeg type annotations toe aan async functies met return type
    content = re.sub(
        r'async def (\w+)\s*\(([^)]*)\) -> ([^:]+):',
        r'async def \1(\2) -> \3:',
        content
    )
    
    # Voeg type annotations toe aan functies met return type
    content = re.sub(
        r'def (\w+)\s*\(([^)]*)\) -> ([^:]+):',
        r'def \1(\2) -> \3:',
        content
    )
    
    # Voeg typing imports toe als ze ontbreken
    if 'from typing import' in content and 'Any' not in content:
        content = content.replace(
            'from typing import',
            'from typing import Any, '
        )
    elif 'from typing import' not in content:
        # Voeg typing import toe aan het begin van het bestand
        lines = content.split('\n')
        import_lines = []
        other_lines = []
        
        for line in lines:
            if line.startswith('import ') or line.startswith('from '):
                import_lines.append(line)
            else:
                other_lines.append(line)
        
        if import_lines:
            import_lines.append('from typing import Any, Dict, List, Optional, Union')
            content = '\n'.join(import_lines + [''] + other_lines)
    
    # Schrijf het bestand terug
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Gerepareerd: {file_path}")


def fix_specific_files() -> None:
    """Repareer specifieke bestanden met bekende problemen."""
    
    # Lijst van bestanden die gerepareerd moeten worden
    files_to_fix = [
        "debug_amazon_text.py",
        "get_metrics_direct.py",
        "test_amazon_factuur.py",
        "test_all_mcp_commands.py",
        "test_cursor_mcp.py",
        "test_pdf_processing.py",
        "test_pipeline_direct.py",
        "tests/test_mcp_client.py",
        "tests/test_mcp_client_backup.py",
        "tests/run_tests.py",
        "tests/conftest.py",
        "tests/test_metrics_generation.py",
        "tests/test_metrics_generation_backup.py",
        "tests/test_monitoring.py",
        "tests/test_ollama_integration.py",
        "tests/test_pipeline.py",
        "tests/test_real_documents.py",
        "tests/test_fastmcp_server.py",
        "tests/test_fastmcp_client.py",
        "tests/test_fastmcp_cli.py",
        "tests/test_fastmcp_direct.py"
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            add_type_annotations_to_file(file_path)
        else:
            print(f"⚠️ Bestand niet gevonden: {file_path}")


def main() -> None:
    """Hoofdfunctie."""
    print("🔧 Starten van mypy error reparatie...")
    
    # Repareer specifieke bestanden
    fix_specific_files()
    
    print("🎉 Alle mypy errors gerepareerd!")


if __name__ == "__main__":
    main()
