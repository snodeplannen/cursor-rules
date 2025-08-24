#!/usr/bin/env python3
"""
Test script voor de MCP Invoice Processor.
Dit script test de verbinding en functionaliteit van de MCP server.
"""

import asyncio
import base64
import json
import sys
from pathlib import Path

# Voeg de src directory toe aan het Python pad
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import mcp
except ImportError:
    print("❌ MCP library niet geïnstalleerd. Installeer met: pip install mcp")
    sys.exit(1)


async def test_mcp_connection():
    """Test de verbinding met de MCP server."""
    print("🔌 Testen van MCP verbinding...")
    
    try:
        # Maak verbinding met de server
        client = mcp.ClientStdio(
            ["C:\\ProgramData\\miniforge3\\Scripts\\uv.exe", "--directory", "C:\\py_cursor-rules\\cursor_ratsenbergertest\\", "run", "python", "-m", "src.mcp_invoice_processor.main"]
        )
        
        # Test de verbinding
        await client.initialize()
        print("✅ MCP verbinding succesvol!")
        
        # Haal server informatie op
        server_info = await client.get_server_info()
        print(f"📋 Server: {server_info.name}")
        print(f"📝 Beschrijving: {server_info.description}")
        
        # Haal beschikbare tools op
        tools = await client.list_tools()
        print(f"🛠️  Beschikbare tools: {len(tools)}")
        
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        return client
        
    except Exception as e:
        print(f"❌ MCP verbinding mislukt: {e}")
        return None


async def test_document_processing(client):
    """Test documentverwerking met een voorbeeld PDF."""
    print("\n📄 Testen van documentverwerking...")
    
    # Maak een eenvoudige test PDF content (dit is geen echte PDF, alleen voor testen)
    test_content = "Dit is een test CV document met ervaring en opleiding informatie."
    test_content_base64 = base64.b64encode(test_content.encode()).decode()
    
    try:
        # Roep de process_document tool aan
        result = await client.call_tool(
            "process_document",
            {
                "file_content_base64": test_content_base64,
                "file_name": "test_cv.pdf"
            }
        )
        
        print("✅ Documentverwerking succesvol!")
        print(f"📊 Resultaat: {json.dumps(result.content, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ Documentverwerking mislukt: {e}")


async def main():
    """Hoofdfunctie voor het testen van de MCP server."""
    print("🚀 MCP Invoice Processor Test Script")
    print("=" * 50)
    
    # Test verbinding
    client = await test_mcp_connection()
    if not client:
        print("❌ Kan niet verder gaan zonder MCP verbinding")
        return
    
    # Test documentverwerking
    await test_document_processing(client)
    
    # Sluit de verbinding
    await client.close()
    print("\n✅ Alle tests voltooid!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test gestopt door gebruiker")
    except Exception as e:
        print(f"\n❌ Onverwachte fout: {e}")
        sys.exit(1)
