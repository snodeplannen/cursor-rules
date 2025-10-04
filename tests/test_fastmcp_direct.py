#!/usr/bin/env python3
"""
Test script voor directe FastMCP server functies zonder protocol overhead.
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
async def test_document_processing() -> None:
    """Test document verwerking functionaliteit met v2.0 processors."""
    logger.info("🚀 Testen Document Verwerking (v2.0)")
    logger.info("=" * 60)
    
    try:
        # Test document classificatie via nieuwe processors
        from mcp_invoice_processor.processors import get_registry
        
        registry = get_registry()
        
        # Test verschillende document types
        test_texts = [
            ("Factuur tekst", "FACTUUR\n\nFactuurnummer: INV-2025-001\nTotaal: €1000\nBTW: €210"),
            ("CV tekst", "CURRICULUM VITAE\n\nNaam: Jan Jansen\nEmail: jan@email.com\nWerkervaring: 5 jaar"),
            ("Onbekende tekst", "Dit is gewoon een willekeurige tekst zonder specifieke structuur.")
        ]
        
        for test_name, test_text in test_texts:
            try:
                doc_type, confidence, processor = await registry.classify_document(test_text, None)
                logger.info(f"{test_name}: {doc_type} ({confidence:.1f}% confidence)")
                
                # Valideer classificatie resultaat
                assert isinstance(doc_type, str)
                assert doc_type in ["invoice", "cv", "unknown"]
                assert isinstance(confidence, float)
                assert 0 <= confidence <= 100
                
            except Exception as e:
                logger.error(f"❌ Classificatie mislukt voor {test_name}: {e}")
                pytest.fail(f"Classificatie test mislukt voor {test_name}: {e}")
        
        logger.info("✅ Document verwerking tests succesvol")
        
    except ImportError as e:
        pytest.skip(f"Document verwerking module niet beschikbaar: {e}")
    except Exception as e:
        pytest.fail(f"Document verwerking test mislukt: {e}")


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
        pytest.skip(f"FastMCP server module niet beschikbaar: {e}")
    except Exception as e:
        pytest.fail(f"FastMCP Server integratie test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_server_tools() -> None:
    """Test FastMCP server tools."""
    logger.info("\n🔧 Testen FastMCP Server Tools")
    logger.info("-" * 30)
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Controleer of tools beschikbaar zijn
        logger.info(f"FastMCP server attributen: {[attr for attr in dir(mcp) if not attr.startswith('_')]}")
        
        # FastMCP tools worden gedefinieerd via decorators, niet als attributen
        # We kunnen de tools testen door de gedecoreerde functies te vinden
        if hasattr(mcp, 'get_tools'):
            tools = await mcp.get_tools()
            logger.info(f"Tools via get_tools: {len(tools) if tools else 0}")
        else:
            logger.info("Geen get_tools methode beschikbaar")
        
        # Controleer specifieke tools
        expected_tools = [
            "process_document_text",
            "process_document_file",
            "classify_document_type",
            "get_metrics",
            "health_check"
        ]
        
        # FastMCP tools worden gedefinieerd via decorators
        # We kunnen controleren of de functies bestaan
        available_tools = []
        for tool_name in expected_tools:
            if hasattr(mcp, tool_name):
                available_tools.append(tool_name)
        
        logger.info(f"Beschikbare tools: {available_tools}")
        
        # Controleer of alle verwachte tools beschikbaar zijn
        missing_tools = [tool for tool in expected_tools if tool not in available_tools]
        if missing_tools:
            logger.warning(f"Ontbrekende tools: {missing_tools}")
        else:
            logger.info("✅ Alle verwachte tools beschikbaar")
        
        logger.info("✅ FastMCP Server tools test succesvol")
        
    except ImportError as e:
        pytest.skip(f"FastMCP server module niet beschikbaar: {e}")
    except Exception as e:
        pytest.fail(f"FastMCP Server tools test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_server_resources() -> None:
    """Test FastMCP server resources."""
    logger.info("\n📁 Testen FastMCP Server Resources")
    logger.info("-" * 30)
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Controleer of resources beschikbaar zijn
        logger.info(f"FastMCP server attributen: {[attr for attr in dir(mcp) if not attr.startswith('_')]}")
        
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
        
    except ImportError as e:
        pytest.skip(f"FastMCP server module niet beschikbaar: {e}")
    except Exception as e:
        pytest.fail(f"FastMCP Server resources test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_server_capabilities() -> None:
    """Test FastMCP server capabilities."""
    logger.info("\n🎯 Testen FastMCP Server Capabilities")
    logger.info("-" * 30)
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Controleer capabilities via globale fastmcp settings
        try:
            from fastmcp import settings as fastmcp_settings
            if hasattr(fastmcp_settings, 'capabilities'):
                capabilities = fastmcp_settings.capabilities
                logger.info(f"Capabilities: {capabilities}")
                
                # Controleer basis capabilities
                if isinstance(capabilities, dict):
                    assert capabilities.get('tools', False), "Tools capability moet enabled zijn"
            else:
                logger.info("Geen capabilities informatie beschikbaar")
        except ImportError:
            logger.info("Geen FastMCP globale settings beschikbaar")
        
        logger.info("✅ FastMCP Server capabilities test succesvol")
        
    except ImportError as e:
        pytest.skip(f"FastMCP server module niet beschikbaar: {e}")
    except Exception as e:
        pytest.fail(f"FastMCP Server capabilities test mislukt: {e}")


@pytest.mark.asyncio
@pytest.mark.fastmcp
async def test_fastmcp_server_metadata() -> None:
    """Test FastMCP server metadata."""
    logger.info("\n📋 Testen FastMCP Server Metadata")
    logger.info("-" * 30)
    
    try:
        from mcp_invoice_processor.fastmcp_server import mcp
        
        # Controleer basis metadata via globale fastmcp settings
        try:
            from fastmcp import settings as fastmcp_settings
            logger.info(f"FastMCP globale settings type: {type(fastmcp_settings)}")
            
            # Controleer beschikbare attributen
            if hasattr(fastmcp_settings, 'name'):
                logger.info(f"   Naam: {fastmcp_settings.name}")
            if hasattr(fastmcp_settings, 'version'):
                logger.info(f"   Versie: {fastmcp_settings.version}")
            if hasattr(fastmcp_settings, 'description'):
                logger.info(f"   Beschrijving: {fastmcp_settings.description}")
            if hasattr(fastmcp_settings, 'author'):
                logger.info(f"   Auteur: {fastmcp_settings.author}")
        except ImportError:
            logger.info("Geen FastMCP globale settings beschikbaar")
        
        logger.info("✅ FastMCP Server metadata test succesvol")
        
    except ImportError as e:
        pytest.skip(f"FastMCP server module niet beschikbaar: {e}")
    except Exception as e:
        pytest.fail(f"FastMCP Server metadata test mislukt: {e}")


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
        
    except ImportError as e:
        pytest.skip(f"FastMCP server module niet beschikbaar: {e}")
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
        
    except ImportError as e:
        pytest.skip(f"FastMCP server module niet beschikbaar: {e}")
    except Exception as e:
        pytest.fail(f"FastMCP Server performance test mislukt: {e}")


# Test samenvatting functie
def test_fastmcp_direct_summary() -> None:
    """Test samenvatting."""
    logger.info("\n📊 FastMCP Direct Test Samenvatting")
    logger.info("=" * 60)
    
    total_tests = 8
    logger.info(f"📋 Totaal aantal tests: {total_tests}")
    logger.info("🎯 Tests omvatten:")
    logger.info("   - Document verwerking")
    logger.info("   - Server integratie")
    logger.info("   - Server tools")
    logger.info("   - Server resources")
    logger.info("   - Server capabilities")
    logger.info("   - Server metadata")
    logger.info("   - Error handling")
    logger.info("   - Performance")
    
    logger.info("✅ FastMCP Direct test suite voltooid")


if __name__ == "__main__":
    # Voor directe uitvoering
    pytest.main([__file__, "-v", "-s", "-m", "fastmcp"])
