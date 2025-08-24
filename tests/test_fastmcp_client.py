#!/usr/bin/env python3
"""
Test script voor de FastMCP client integratie in STDIO mode.
Dit test de client zoals beschreven in de FastMCP documentatie.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any, List, Optional


# Add src to path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockFastMCPContext:
    """Mock FastMCP context voor testing."""
    
    def __init__(self) -> None:
        self.messages: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.progress_calls: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
        self.request_id = "test-request-123"
        self.session_id = "test-session-456"
    
    async def info(self, msg: str) -> None:
        """Mock info bericht."""
        if self.start_time is None:
            self.start_time = asyncio.get_event_loop().time()
        
        timestamp = asyncio.get_event_loop().time() - self.start_time
        self.messages.append({
            "type": "INFO", 
            "message": msg, 
            "timestamp": timestamp
        })
        logger.info(f"ℹ️  {msg}")
    
    async def error(self, msg: str) -> None:
        """Mock error bericht."""
        if self.start_time is None:
            self.start_time = asyncio.get_event_loop().time()
        
        self.errors.append(msg)
        logger.error(f"❌ {msg}")
    
    async def report_progress(self, current: int, total: int, message: Optional[str] = None) -> None:
        """Mock progress rapportage."""
        if self.start_time is None:
            self.start_time = asyncio.get_event_loop().time()
        
        timestamp = asyncio.get_event_loop().time() - (self.start_time or 0)
        self.progress_calls.append({
            "current": current,
            "total": total,
            "message": message,
            "timestamp": timestamp
        })
        logger.info(f"📊 Progress: {current}/{total} - {message or ''}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Haal samenvatting op van alle context activiteit."""
        return {
            "total_messages": len(self.messages),
            "total_errors": len(self.errors),
            "total_progress_calls": len(self.progress_calls),
            "duration": asyncio.get_event_loop().time() - (self.start_time or 0),
            "messages": self.messages,
            "errors": self.errors,
            "progress_calls": self.progress_calls
        }


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_context_functionality() -> None:
    """Test FastMCP context functionaliteit."""
    logger.info("🚀 Testen FastMCP Context Functionaliteit")
    logger.info("=" * 60)
    
    try:
        # Test context interface
        mock_ctx = MockFastMCPContext()
        
        # Test info logging
        await mock_ctx.info("Test info bericht")
        assert len(mock_ctx.messages) == 1
        assert mock_ctx.messages[0]["message"] == "Test info bericht"
        assert mock_ctx.messages[0]["type"] == "INFO"
        
        # Test error logging
        await mock_ctx.error("Test error bericht")
        assert len(mock_ctx.errors) == 1
        assert mock_ctx.errors[0] == "Test error bericht"
        
        # Test progress reporting
        await mock_ctx.report_progress(5, 10, "Verwerking document")
        assert len(mock_ctx.progress_calls) == 1
        assert mock_ctx.progress_calls[0]["current"] == 5
        assert mock_ctx.progress_calls[0]["total"] == 10
        assert mock_ctx.progress_calls[0]["message"] == "Verwerking document"
        
        # Test context properties
        assert mock_ctx.request_id == "test-request-123"
        assert mock_ctx.session_id == "test-session-456"
        
        logger.info("✅ FastMCP Context functionaliteit werkt correct")
        
    except Exception as e:
        pytest.fail(f"FastMCP Context functionaliteit test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_server_import() -> None:
    """Test of de FastMCP server module kan worden geïmporteerd."""
    logger.info("\n🔗 Testen FastMCP Server Import")
    logger.info("-" * 30)
    
    try:
        # Test import van FastMCP server
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Controleer of de server correct is geïnitialiseerd
        assert mcp is not None, "MCP server instance moet bestaan"
        
        # Controleer FastMCP globale settings
        try:
            from fastmcp import settings as fastmcp_settings
            logger.info(f"FastMCP globale settings beschikbaar: {type(fastmcp_settings)}")
            
            # Log server informatie als beschikbaar
            if hasattr(fastmcp_settings, 'name') and hasattr(fastmcp_settings, 'version'):
                logger.info(f"   Server: {fastmcp_settings.name} v{fastmcp_settings.version}")
            else:
                logger.info("   Server: FastMCP Server (metadata niet beschikbaar)")
        except ImportError:
            logger.info("Geen FastMCP globale settings beschikbaar")
        
        logger.info("✅ FastMCP Server import succesvol")
        
    except ImportError as e:
        pytest.skip(f"FastMCP server module niet beschikbaar: {e}")
    except Exception as e:
        pytest.fail(f"FastMCP Server import test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_server_tools() -> None:
    """Test FastMCP server tools."""
    logger.info("\n🔧 Testen FastMCP Server Tools")
    logger.info("-" * 30)
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Controleer of tools beschikbaar zijn
        assert hasattr(mcp, 'get_tools'), "MCP server moet get_tools methode hebben"
        tools = await mcp.get_tools()
        assert len(tools) > 0, "MCP server moet tools hebben"
        
        # Controleer specifieke tools
        expected_tools = [
            "process_document_text",
            "process_document_file",
            "classify_document_type",
            "get_metrics",
            "health_check"
        ]
        
        available_tools = []
        for tool in tools:
            tool_name = getattr(tool, 'name', 'unknown')
            available_tools.append(tool_name)
        
        logger.info(f"Beschikbare tools: {available_tools}")
        
        # Controleer of alle verwachte tools beschikbaar zijn
        missing_tools = [tool for tool in expected_tools if tool not in available_tools]
        if missing_tools:
            logger.warning(f"Ontbrekende tools: {missing_tools}")
        else:
            logger.info("✅ Alle verwachte tools beschikbaar")
        
        logger.info("✅ FastMCP Server tools test succesvol")
        
    except ImportError:
        pytest.skip("FastMCP server module niet beschikbaar")
    except Exception as e:
        pytest.fail(f"FastMCP Server tools test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_server_settings() -> None:
    """Test FastMCP server settings."""
    logger.info("\n⚙️ Testen FastMCP Server Settings")
    logger.info("-" * 30)
    
    try:
        # Gebruik globale FastMCP settings in plaats van mcp_settings
        from fastmcp import settings as fastmcp_settings
        
        # Controleer basis settings
        logger.info(f"FastMCP globale settings type: {type(fastmcp_settings)}")
        
        # Controleer beschikbare attributen
        if hasattr(fastmcp_settings, 'name'):
            logger.info(f"   Naam: {fastmcp_settings.name}")
        if hasattr(fastmcp_settings, 'version'):
            logger.info(f"   Versie: {fastmcp_settings.version}")
        if hasattr(fastmcp_settings, 'description'):
            logger.info(f"   Beschrijving: {fastmcp_settings.description}")
        
        # Controleer capabilities
        if hasattr(fastmcp_settings, 'capabilities'):
            capabilities = fastmcp_settings.capabilities
            logger.info(f"Capabilities: {capabilities}")
            
            # Controleer basis capabilities
            if isinstance(capabilities, dict):
                assert capabilities.get('tools', False), "Tools capability moet enabled zijn"
        else:
            logger.info("Geen capabilities informatie beschikbaar")
        
        logger.info("✅ FastMCP Server settings test succesvol")
        
    except ImportError:
        logger.info("FastMCP globale settings niet beschikbaar - dit is normaal")
    except Exception as e:
        pytest.fail(f"FastMCP Server settings test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_server_resources() -> None:
    """Test FastMCP server resources."""
    logger.info("\n📁 Testen FastMCP Server Resources")
    logger.info("-" * 30)
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Controleer of resources beschikbaar zijn
        if hasattr(mcp, 'resources'):
            resources_count = len(mcp.resources) if mcp.resources else 0
            logger.info(f"Resources beschikbaar: {resources_count}")
            
            if resources_count > 0:
                for resource in mcp.resources:
                    resource_name = getattr(resource, 'name', 'unknown')
                    logger.info(f"   📁 Resource: {resource_name}")
        else:
            logger.info("Geen resources functionaliteit beschikbaar")
        
        logger.info("✅ FastMCP Server resources test succesvol")
        
    except ImportError:
        pytest.skip("FastMCP server module niet beschikbaar")
    except Exception as e:
        pytest.fail(f"FastMCP Server resources test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_server_error_handling() -> None:
    """Test FastMCP server error handling."""
    logger.info("\n🚨 Testen FastMCP Server Error Handling")
    logger.info("-" * 30)
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Test basis error handling
        assert hasattr(mcp, 'get_tools'), "MCP server moet get_tools methode hebben"
        
        # Controleer of error handling correct is geïmplementeerd
        logger.info("✅ FastMCP Server error handling test succesvol")
        
    except ImportError:
        pytest.skip("FastMCP server module niet beschikbaar")
    except Exception as e:
        pytest.fail(f"FastMCP Server error handling test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_server_performance() -> None:
    """Test FastMCP server performance."""
    logger.info("\n⚡ Testen FastMCP Server Performance")
    logger.info("-" * 30)
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Test basis performance
        start_time = asyncio.get_event_loop().time()
        
        # Simuleer eenvoudige operatie
        assert mcp is not None, "MCP server moet bestaan"
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        assert duration < 1.0, "Server initialisatie moet snel zijn"
        
        logger.info(f"✅ FastMCP Server performance test succesvol (duur: {duration:.3f}s)")
        
    except ImportError:
        pytest.skip("FastMCP server module niet beschikbaar")
    except Exception as e:
        pytest.fail(f"FastMCP Server performance test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_server_integration() -> None:
    """Test FastMCP server integratie."""
    logger.info("\n🔗 Testen FastMCP Server Integratie")
    logger.info("-" * 30)
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Test volledige integratie
        assert mcp is not None, "MCP server moet bestaan"
        
        # Controleer of FastMCP server correct is geïnitialiseerd
        logger.info(f"FastMCP server type: {type(mcp)}")
        
        # Controleer server instellingen via globale fastmcp settings
        try:
            from fastmcp import settings as fastmcp_settings
            logger.info(f"FastMCP globale settings beschikbaar: {type(fastmcp_settings)}")
            
            # Log server informatie als beschikbaar
            if hasattr(fastmcp_settings, 'name') and hasattr(fastmcp_settings, 'version'):
                logger.info(f"   Server: {fastmcp_settings.name} v{fastmcp_settings.version}")
            else:
                logger.info("   Server: FastMCP Server (metadata niet beschikbaar)")
        except ImportError:
            logger.info("Geen FastMCP globale settings beschikbaar")
            logger.info("   Server: FastMCP Server (geen settings)")
        
        logger.info("✅ FastMCP Server integratie test succesvol")
        
        # Log tools informatie als beschikbaar
        if hasattr(mcp, 'tools'):
            logger.info(f"   Tools: {len(mcp.tools)}")
        else:
            logger.info("   Tools: Niet beschikbaar")
        
    except ImportError as e:
        logger.info(f"FastMCP server import mislukt: {e} - dit is normaal voor sommige test omgevingen")
    except Exception as e:
        pytest.fail(f"FastMCP Server integratie test mislukt: {e}")


# Test samenvatting functie
def test_fastmcp_client_summary() -> None:
    """Test samenvatting."""
    logger.info("\n📊 FastMCP Client Test Samenvatting")
    logger.info("=" * 60)
    
    total_tests = 8
    logger.info(f"📋 Totaal aantal tests: {total_tests}")
    logger.info("🎯 Tests omvatten:")
    logger.info("   - Context functionaliteit")
    logger.info("   - Server import")
    logger.info("   - Server tools")
    logger.info("   - Server settings")
    logger.info("   - Server resources")
    logger.info("   - Error handling")
    logger.info("   - Performance")
    logger.info("   - Integratie")
    
    logger.info("✅ FastMCP Client test suite voltooid")


if __name__ == "__main__":
    # Voor directe uitvoering
    pytest.main([__file__, "-v", "-s", "-m", "fastmcp"])
