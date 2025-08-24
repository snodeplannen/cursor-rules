#!/usr/bin/env python3
"""
Eenvoudige MCP Server voor document verwerking.
Gebaseerd op de officiële MCP Python SDK voor betrouwbaarheid.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

# Voeg src toe aan Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Gebruik de beschikbare MCP packages
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource
    )
    MCP_AVAILABLE = True
except ImportError:
    # Fallback naar eenvoudigere implementatie
    MCP_AVAILABLE = False
    print("MCP packages niet beschikbaar, gebruik fallback implementatie")

from mcp_invoice_processor.processing.pipeline import extract_structured_data
from mcp_invoice_processor.processing.classification import classify_document
from mcp_invoice_processor.processing.models import CVData, InvoiceData
from mcp_invoice_processor.config import settings as app_settings
from mcp_invoice_processor.monitoring.metrics import metrics_collector
from mcp_invoice_processor.logging_config import setup_logging

# Configureer logging
logger = setup_logging(log_level=app_settings.LOG_LEVEL)

# Tool definities
TOOLS = [
    {
        "name": "process_document_text",
        "description": "Verwerk document tekst en extraheer gestructureerde data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "De tekst inhoud van het document"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "process_document_file",
        "description": "Verwerk een document bestand (PDF, TXT) en extraheer data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Pad naar het document bestand"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "classify_document_type",
        "description": "Classificeer alleen het document type",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "De tekst inhoud van het document"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "get_metrics",
        "description": "Haal huidige performance metrics op",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "health_check",
        "description": "Controleer service gezondheid",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

async def handle_list_tools() -> Dict[str, Any]:
    """Lijst alle beschikbare tools op."""
    logger.info("Tools opgevraagd")
    return {"tools": TOOLS}

async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Voer een tool uit."""
    logger.info(f"Tool aangeroepen: {name} met argumenten: {arguments}")
    
    try:
        if name == "process_document_text":
            text = arguments.get("text", "")
            if not text.strip():
                return {
                    "content": [{"type": "text", "text": "Fout: Document tekst mag niet leeg zijn"}]
                }
            
            # Classificeer document type
            doc_type = classify_document(text)
            logger.info(f"Document geclassificeerd als: {doc_type}")
            
            # Extraheer gestructureerde data (default JSON schema mode)
            from src.mcp_invoice_processor.processing.pipeline import ExtractionMethod
            extracted_data = await extract_structured_data(text, doc_type, None, ExtractionMethod.JSON_SCHEMA)
            logger.info(f"Data geëxtraheerd: {extracted_data}")
            
            # Update metrics
            metrics_collector.record_document_processing(success=True)
            
            result = {
                "document_type": doc_type,
                "extracted_data": extracted_data,
                "processing_status": "success"
            }
            
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
            }
            
        elif name == "process_document_file":
            file_path = arguments.get("file_path", "")
            if not file_path:
                return {
                    "content": [{"type": "text", "text": "Fout: Bestandspad is vereist"}]
                }
            
            # Hier zou je bestand verwerking implementeren
            # Voor nu returnen we een placeholder
            result = {
                "file_path": file_path,
                "status": "file_processing_not_implemented",
                "message": "Bestand verwerking wordt nog geïmplementeerd"
            }
            
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
            }
            
        elif name == "classify_document_type":
            text = arguments.get("text", "")
            if not text.strip():
                return {
                    "content": [{"type": "text", "text": "Fout: Document tekst mag niet leeg zijn"}]
                }
            
            doc_type = classify_document(text)
            logger.info(f"Document geclassificeerd als: {doc_type}")
            
            result = {
                "document_type": doc_type,
                "confidence": "high"
            }
            
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
            }
            
        elif name == "get_metrics":
            metrics = metrics_collector.get_metrics()
            logger.info(f"Metrics opgevraagd: {metrics}")
            
            return {
                "content": [{"type": "text", "text": json.dumps(metrics, indent=2, ensure_ascii=False)}]
            }
            
        elif name == "health_check":
            # Controleer Ollama
            import httpx
            ollama_status = "unknown"
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
                    ollama_status = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception as e:
                ollama_status = f"error: {str(e)}"
            
            health_status = {
                "server": "healthy",
                "ollama": ollama_status,
                "timestamp": str(Path(__file__).stat().st_mtime)
            }
            
            logger.info(f"Health check uitgevoerd: {health_status}")
            
            return {
                "content": [{"type": "text", "text": json.dumps(health_status, indent=2, ensure_ascii=False)}]
            }
            
        else:
            return {
                "content": [{"type": "text", "text": f"Onbekende tool: {name}"}]
            }
            
    except Exception as e:
        logger.error(f"Fout bij uitvoeren tool {name}: {e}")
        metrics_collector.record_document_processing(success=False)
        
        return {
            "content": [{"type": "text", "text": f"Fout bij uitvoeren tool: {str(e)}"}]
        }

async def handle_mcp_request():
    """Handle MCP requests via stdio."""
    try:
        # Lees input van stdin
        line = sys.stdin.readline()
        if not line:
            return
        
        request = json.loads(line)
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"MCP request: {method}")
        
        # Handle verschillende methoden
        if method == "tools/list":
            result = await handle_list_tools()
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            result = await handle_call_tool(tool_name, tool_args)
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
        
        # Schrijf response naar stdout
        print(json.dumps(response), flush=True)
        
    except Exception as e:
        logger.error(f"Error handling MCP request: {e}")
        error_response = {
            "jsonrpc": "2.0",
            "id": request_id if 'request_id' in locals() else None,
            "error": {"code": -32603, "message": str(e)}
        }
        print(json.dumps(error_response), flush=True)

async def main():
    """Start de MCP server."""
    logger.info("🚀 Eenvoudige MCP Server gestart")
    
    if MCP_AVAILABLE:
        # Gebruik officiële MCP server als beschikbaar
        server = Server("mcp-invoice-processor")
        
        @server.list_tools()
        async def list_tools() -> Dict[str, Any]:
            return await handle_list_tools()
        
        @server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
            return await handle_call_tool(name, arguments)
        
        # Start de server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-invoice-processor",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )
    else:
        # Fallback naar eenvoudige stdio implementatie
        logger.info("Gebruik fallback stdio implementatie")
        while True:
            try:
                await handle_mcp_request()
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server gestopt door gebruiker")
    except Exception as e:
        logger.error(f"Server fout: {e}")
        sys.exit(1)
