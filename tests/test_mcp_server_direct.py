#!/usr/bin/env python3
"""
Directe test van de MCP server.
"""
import pytest

import asyncio
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_mcp_server_direct():
    """Test de MCP server direct."""
    logger.info("🧪 Directe test van MCP server")
    
    try:
        # Import de server
        from mcp_invoice_processor.fastmcp_server import mcp
        
        logger.info(f"✅ MCP server geïmporteerd: {type(mcp)}")
        logger.info(f"   MCP object: {mcp}")
        
        # Test alle attributen
        logger.info("\n🔍 MCP Server Attributen:")
        
        # Basis attributen
        for attr in ['name', 'version', 'description', 'author', 'contact', 'license']:
            if hasattr(mcp, attr):
                value = getattr(mcp, attr)
                logger.info(f"   {attr}: {value}")
            else:
                logger.info(f"   {attr}: ❌ Niet gevonden")
        
        # Tools
        if hasattr(mcp, 'tools'):
            tools = getattr(mcp, 'tools')
            logger.info(f"   tools: {type(tools)} - {len(tools) if hasattr(tools, '__len__') else 'Geen lengte'}")
            
            if hasattr(tools, '__len__') and len(tools) > 0:
                for i, tool in enumerate(tools):
                    logger.info(f"      Tool {i+1}: {tool}")
                    if hasattr(tool, 'name'):
                        logger.info(f"         Naam: {tool.name}")
                    if hasattr(tool, 'description'):
                        logger.info(f"         Beschrijving: {tool.description}")
        else:
            logger.info("   tools: ❌ Niet gevonden")
        
        # Resources
        if hasattr(mcp, 'resources'):
            resources = getattr(mcp, 'resources')
            logger.info(f"   resources: {type(resources)} - {len(resources) if hasattr(resources, '__len__') else 'Geen lengte'}")
            
            if hasattr(resources, '__len__') and len(resources) > 0:
                for i, resource in enumerate(resources):
                    logger.info(f"      Resource {i+1}: {resource}")
                    if hasattr(resource, 'name'):
                        logger.info(f"         Naam: {resource.name}")
        else:
            logger.info("   resources: ❌ Niet gevonden")
        
        # Prompts
        if hasattr(mcp, 'prompts'):
            prompts = getattr(mcp, 'prompts')
            logger.info(f"   prompts: {type(prompts)} - {len(prompts) if hasattr(prompts, '__len__') else 'Geen lengte'}")
            
            if hasattr(prompts, '__len__') and len(prompts) > 0:
                for i, prompt in enumerate(prompts):
                    logger.info(f"      Prompt {i+1}: {prompt}")
                    if hasattr(prompt, 'name'):
                        logger.info(f"         Naam: {prompt.name}")
        else:
            logger.info("   prompts: ❌ Niet gevonden")
        
        # Test alle attributen van het mcp object
        logger.info("\n🔍 Alle MCP Object Attributen:")
        for attr_name in dir(mcp):
            if not attr_name.startswith('_') and attr_name != 'settings':  # Skip deprecated settings
                try:
                    attr_value = getattr(mcp, attr_name)
                    if not callable(attr_value):
                        logger.info(f"   {attr_name}: {type(attr_value)} = {attr_value}")
                except Exception as e:
                    logger.info(f"   {attr_name}: ❌ Error bij ophalen: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP server test mislukt: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_fastmcp_import():
    """Test FastMCP import en basis functionaliteit."""
    logger.info("🧪 Testen FastMCP Import")
    
    try:
        import fastmcp
        logger.info(f"✅ FastMCP geïmporteerd: {fastmcp}")
        logger.info(f"   Versie: {getattr(fastmcp, '__version__', 'Onbekend')}")
        
        # Test FastMCP.Server
        if hasattr(fastmcp, 'Server'):
            logger.info(f"✅ FastMCP.Server beschikbaar: {fastmcp.Server}")
        else:
            logger.info("❌ FastMCP.Server niet gevonden")
        
        # Test FastMCP.Context
        if hasattr(fastmcp, 'Context'):
            logger.info(f"✅ FastMCP.Context beschikbaar: {fastmcp.Context}")
        else:
            logger.info("❌ FastMCP.Context niet gevonden")
        
        # Test alle FastMCP attributen
        logger.info("\n🔍 FastMCP Module Attributen:")
        for attr_name in dir(fastmcp):
            if not attr_name.startswith('_'):
                try:
                    attr_value = getattr(fastmcp, attr_name)
                    if not callable(attr_value):
                        logger.info(f"   {attr_name}: {type(attr_value)} = {attr_value}")
                except Exception as e:
                    logger.info(f"   {attr_name}: ❌ Error bij ophalen: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FastMCP import test mislukt: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Hoofdfunctie."""
    logger.info("🚀 Starten van directe MCP server tests...")
    
    tests = [
        ("FastMCP Import", test_fastmcp_import),
        ("MCP Server Direct", test_mcp_server_direct),
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 STARTING: {test_name}")
        logger.info(f"{'='*60}")
        
        try:
            success = await test_func()
            logger.info(f"✅ {test_name}: {'GESLAAGD' if success else 'GEFAALD'}")
        except Exception as e:
            logger.error(f"❌ {test_name}: CRASH - {e}")
    
    logger.info("\n🏁 Alle tests voltooid")


if __name__ == "__main__":
    asyncio.run(main())
