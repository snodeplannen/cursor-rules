#!/usr/bin/env python3
"""
Eenvoudige test om te controleren of de MCP server werkt.
"""
import sys
import os
import asyncio

# Voeg src directory toe aan Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_mcp_import():
    """Test of de MCP modules kunnen worden geïmporteerd."""
    try:
        print("🧪 Test MCP Import...")
        
        # Test main module
        from src.mcp_invoice_processor.main import mcp
        print("✅ MCP main module geïmporteerd")
        
        # Test tools (async call)
        tools = await mcp.get_tools()
        print(f"✅ MCP tools gevonden: {len(tools)} tools")
        
        # Toon tool informatie
        for i, tool in enumerate(tools):
            if hasattr(tool, 'name'):
                print(f"   - {tool.name}: {tool.description}")
            else:
                print(f"   - Tool {i+1}: {tool}")
        
        # Test metrics
        from src.mcp_invoice_processor.monitoring.metrics import metrics_collector
        print("✅ Metrics module geïmporteerd")
        
        # Haal metrics op
        metrics = metrics_collector.get_comprehensive_metrics()
        print("✅ Metrics opgehaald")
        print(f"   - Systeem: {metrics['system']['uptime']}")
        print(f"   - Documenten: {metrics['processing']['total_documents']}")
        print(f"   - Ollama: {metrics['ollama']['total_requests']}")
        
        print("\n🎉 Alle MCP tests geslaagd!")
        return True
        
    except Exception as e:
        print(f"❌ MCP test gefaald: {e}")
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
        success = loop.run_until_complete(test_mcp_import())
        
        # Sluit loop
        loop.close()
        
        return success
        
    except Exception as e:
        print(f"❌ Test uitvoering gefaald: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
