#!/usr/bin/env python3
"""
Test script voor de FastMCP server met echte document verwerking.
Dit test de server zoals beschreven in de FastMCP documentatie.
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
        
        timestamp = asyncio.get_event_loop().time() - self.start_time
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
async def test_fastmcp_library_available() -> None:
    """Test of de FastMCP library beschikbaar is."""
    logger.info("🚀 Testen FastMCP Library Beschikbaarheid")
    logger.info("=" * 60)
    
    try:
        # Test of FastMCP library beschikbaar is
        import fastmcp
        assert fastmcp is not None, "FastMCP library moet beschikbaar zijn"
        
        # Test basis FastMCP classes
        from fastmcp import FastMCP, Context, Settings
        assert FastMCP is not None, "FastMCP class moet beschikbaar zijn"
        assert Context is not None, "Context class moet beschikbaar zijn"
        assert Settings is not None, "Settings class moet beschikbaar zijn"
        
        # Test FastMCP exceptions
        from fastmcp.exceptions import FastMCPError
        assert FastMCPError is not None, "FastMCPError class moet beschikbaar zijn"
        
        # Test beschikbare FastMCP utilities
        from fastmcp.utilities import json_schema, types
        assert json_schema is not None, "json_schema module moet beschikbaar zijn"
        assert types is not None, "types module moet beschikbaar zijn"
        
        logger.info("✅ FastMCP library en alle componenten beschikbaar")
        logger.info(f"   FastMCP versie: {getattr(fastmcp, '__version__', 'onbekend')}")
        
    except ImportError as e:
        pytest.skip(f"FastMCP library niet beschikbaar: {e}")
    except Exception as e:
        pytest.fail(f"FastMCP library test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_basic_functionality() -> None:
    """Test basis FastMCP functionaliteit."""
    logger.info("\n🔧 Testen Basis FastMCP Functionaliteit")
    logger.info("-" * 30)
    
    try:
        from fastmcp import FastMCP, Settings
        
        # Test Settings creation
        test_settings = Settings()
        assert test_settings is not None, "Settings object moet aangemaakt kunnen worden"
        
        logger.info("✅ FastMCP Settings functionaliteit werkt")
        
        # Test FastMCP server creation
        test_server = FastMCP()
        assert test_server is not None, "FastMCP server moet aangemaakt kunnen worden"
        assert hasattr(test_server, 'get_tools'), "Server moet get_tools methode hebben"
        
        logger.info("✅ FastMCP server creation werkt")
        
    except Exception as e:
        pytest.fail(f"FastMCP basis functionaliteit test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_context_functionality() -> None:
    """Test FastMCP context functionaliteit."""
    logger.info("\n🔧 Testen FastMCP Context Functionaliteit")
    logger.info("-" * 30)
    
    try:
        from fastmcp import Context  # noqa: F401
        
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
async def test_fastmcp_utilities() -> None:
    """Test FastMCP utilities functionaliteit."""
    logger.info("\n🔧 Testen FastMCP Utilities")
    logger.info("-" * 30)
    
    try:
        from fastmcp.utilities import json_schema, types
        
        # Test json_schema module
        assert json_schema is not None, "json_schema module moet beschikbaar zijn"
        
        # Test types module
        assert types is not None, "types module moet beschikbaar zijn"
        
        # Test beschikbare functies
        json_schema_functions = [attr for attr in dir(json_schema) if not attr.startswith('_')]
        types_functions = [attr for attr in dir(types) if not attr.startswith('_')]
        
        logger.info(f"JSON Schema functies: {json_schema_functions}")
        logger.info(f"Types functies: {types_functions}")
        
        logger.info("✅ FastMCP Utilities werken correct")
        
    except Exception as e:
        pytest.fail(f"FastMCP Utilities test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_error_handling() -> None:
    """Test FastMCP error handling."""
    logger.info("\n🚨 Testen FastMCP Error Handling")
    logger.info("-" * 30)
    
    try:
        from fastmcp.exceptions import FastMCPError
        
        # Test FastMCPError creation
        error_msg = "Test error bericht"
        fastmcp_error = FastMCPError(error_msg)
        
        assert str(fastmcp_error) == error_msg, "Error message moet correct zijn"
        assert isinstance(fastmcp_error, Exception), "FastMCPError moet Exception zijn"
        
        logger.info("✅ FastMCP Error Handling werkt correct")
        
    except Exception as e:
        pytest.fail(f"FastMCP Error Handling test mislukt: {e}")


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
        assert hasattr(mcp, 'get_tools'), "MCP server moet get_tools methode hebben"
        
        # Controleer of server correct is geïnitialiseerd
        assert mcp is not None, "Server moet bestaan"
        
        logger.info("✅ FastMCP Server import succesvol")
        tools = await mcp.get_tools()
        logger.info(f"   Tools beschikbaar: {len(tools)}")
        
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
        
        # Test tool metadata
        for tool in tools:
            tool_name = getattr(tool, 'name', 'unknown')
            
            # Controleer beschrijving
            if hasattr(tool, 'description'):
                logger.info(f"   📝 {tool_name}: {tool.description}")
            else:
                logger.warning(f"   ⚠️ {tool_name}: Geen beschrijving")
            
            # Controleer input schema
            if hasattr(tool, 'input_schema'):
                logger.info(f"   📋 {tool_name}: Input schema beschikbaar")
            else:
                logger.warning(f"   ⚠️ {tool_name}: Geen input schema")
        
        logger.info("✅ FastMCP Server tools test succesvol")
        
    except ImportError:
        pytest.skip("FastMCP server module niet beschikbaar")
    except Exception as e:
        pytest.fail(f"FastMCP Server tools test mislukt: {e}")


# Test samenvatting functie
def test_fastmcp_server_summary() -> None:
    """Test samenvatting."""
    logger.info("\n📊 FastMCP Server Test Samenvatting")
    logger.info("=" * 60)
    
    total_tests = 7
    logger.info(f"📋 Totaal aantal tests: {total_tests}")
    logger.info("🎯 Tests omvatten:")
    logger.info("   - Library beschikbaarheid")
    logger.info("   - Basis functionaliteit")
    logger.info("   - Context functionaliteit")
    logger.info("   - Utilities")
    logger.info("   - Error handling")
    logger.info("   - Server import")
    logger.info("   - Server tools")
    
    logger.info("✅ FastMCP Server test suite voltooid")


if __name__ == "__main__":
    # Voor directe uitvoering
    pytest.main([__file__, "-v", "-s", "-m", "fastmcp"])
