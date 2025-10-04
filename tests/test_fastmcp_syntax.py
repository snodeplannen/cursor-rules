#!/usr/bin/env python3
"""
Test FastMCP syntax en functionaliteit.
"""
import pytest

import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_fastmcp_basic():
    """Test basis FastMCP functionaliteit."""
    logger.info("🧪 Testen basis FastMCP functionaliteit")
    
    try:
        from fastmcp import FastMCP, Context
        
        # Test basis FastMCP server
        server = FastMCP(
            name="Test Server",
            version="1.0.0"
        )
        
        logger.info(f"✅ FastMCP server aangemaakt: {server}")
        logger.info(f"   Naam: {server.name}")
        logger.info(f"   Versie: {server.version}")
        
        # Test tool decorator
        @server.tool(
            name="test_tool",
            description="Een test tool"
        )
        async def test_tool(text: str, ctx: Context) -> str:
            return f"Test resultaat: {text}"
        
        logger.info("✅ Tool decorator toegevoegd")
        
        # Test resource decorator
        @server.resource("test://example")
        async def test_resource() -> str:
            return "Test resource inhoud"
        
        logger.info("✅ Resource decorator toegevoegd")
        
        # Test prompt decorator
        @server.prompt("test-prompt")
        async def test_prompt(topic: str = "general") -> str:
            return f"Test prompt voor topic: {topic}"
        
        logger.info("✅ Prompt decorator toegevoegd")
        
        # Test server eigenschappen
        logger.info("\n🔍 Server Eigenschappen:")
        
        # Tools
        if hasattr(server, 'tools'):
            tools = getattr(server, 'tools')
            logger.info(f"   tools: {type(tools)} - {len(tools) if hasattr(tools, '__len__') else 'Geen lengte'}")
        else:
            logger.info("   tools: ❌ Niet gevonden")
        
        # Resources
        if hasattr(server, 'resources'):
            resources = getattr(server, 'resources')
            logger.info(f"   resources: {type(resources)} - {len(resources) if hasattr(resources, '__len__') else 'Geen lengte'}")
        else:
            logger.info("   resources: ❌ Niet gevonden")
        
        # Prompts
        if hasattr(server, 'prompts'):
            prompts = getattr(server, 'prompts')
            logger.info(f"   prompts: {type(prompts)} - {len(prompts) if hasattr(prompts, '__len__') else 'Geen lengte'}")
        else:
            logger.info("   prompts: ❌ Niet gevonden")
        
        # Test alle attributen (skip deprecated settings)
        logger.info("\n🔍 Alle Server Attributen:")
        for attr_name in dir(server):
            if not attr_name.startswith('_') and attr_name != 'settings':  # Skip deprecated settings
                try:
                    attr_value = getattr(server, attr_name)
                    if not callable(attr_value):
                        logger.info(f"   {attr_name}: {type(attr_value)} = {attr_value}")
                except Exception as e:
                    logger.info(f"   {attr_name}: ❌ Error bij ophalen: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FastMCP test mislukt: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Hoofdfunctie."""
    logger.info("🚀 Starten van FastMCP syntax tests...")
    
    success = await test_fastmcp_basic()
    
    if success:
        logger.info("✅ FastMCP syntax test geslaagd")
    else:
        logger.error("❌ FastMCP syntax test gefaald")


if __name__ == "__main__":
    asyncio.run(main())
