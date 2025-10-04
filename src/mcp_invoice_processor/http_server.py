#!/usr/bin/env python3
"""
FastMCP HTTP Server voor de MCP Document Processor.
Integreert MCP functionaliteit met HTTP custom routes voor monitoring.
"""

import warnings
import sys
from pathlib import Path

# Voeg src directory toe aan Python path voor standalone execution
if __name__ == "__main__":
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from fastmcp import FastMCP
from mcp_invoice_processor.monitoring.metrics import metrics_collector
from mcp_invoice_processor.logging_config import setup_logging
from mcp_invoice_processor import tools

# Onderdruk warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Setup logging
logger = setup_logging(log_level="INFO")

# Maak FastMCP server met HTTP transport ondersteuning en importeer tools
mcp = FastMCP(
    name="MCP Document Processor HTTP Server",
    instructions="""
    Deze server biedt document verwerking via MCP tools en HTTP monitoring endpoints.
    
    MCP Tools:
    - process_document_text: Verwerk document tekst
    - process_document_file: Verwerk document bestand  
    - classify_document_type: Classificeer document type
    - get_metrics: Haal server metrics op
    - health_check: Controleer server status
    
    HTTP Endpoints:
    - /health: Health check
    - /metrics: JSON metrics
    - /metrics/prometheus: Prometheus metrics
    """
)

# Registreer de gedeelde tools
mcp.tool()(tools.process_document_text)
mcp.tool()(tools.process_document_file)
mcp.tool()(tools.classify_document_type)
mcp.tool()(tools.get_metrics)
mcp.tool()(tools.health_check)

@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    """Root endpoint met server informatie."""
    return JSONResponse({
        "name": "MCP Invoice Processor HTTP Server",
        "version": "1.0.0",
        "status": "running",
        "transport": "HTTP",
        "mcp_version": "1.13.1",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics", 
            "metrics_prometheus": "/metrics/prometheus",
            "mcp": "/mcp"
        },
        "mcp_tools": [
            "process_document_text",
            "process_document_file",
            "classify_document_type", 
            "get_metrics",
            "health_check"
        ]
    })

@mcp.custom_route("/health", methods=["GET"])
async def health_endpoint(request: Request) -> JSONResponse:
    """HTTP Health check endpoint."""
    try:
        # Gebruik de gedeelde health_check tool
        health_result = await tools.health_check()
        
        if health_result.get("status") == "healthy":
            return JSONResponse(health_result)
        else:
            return JSONResponse(health_result, status_code=503)
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e),
            "service": "MCP Invoice Processor HTTP Server"
        }, status_code=503)

@mcp.custom_route("/metrics", methods=["GET"])
async def metrics_endpoint(request: Request) -> JSONResponse:
    """HTTP Metrics endpoint in JSON formaat."""
    try:
        metrics = metrics_collector.get_comprehensive_metrics()
        return JSONResponse(metrics)
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return JSONResponse({
            "error": f"Failed to get metrics: {str(e)}"
        }, status_code=500)

@mcp.custom_route("/metrics/prometheus", methods=["GET"])
async def prometheus_metrics_endpoint(request: Request) -> PlainTextResponse:
    """HTTP Metrics endpoint in Prometheus formaat."""
    try:
        prometheus_metrics = metrics_collector.export_metrics("prometheus")
        return PlainTextResponse(prometheus_metrics)
    except Exception as e:
        logger.error(f"Failed to get Prometheus metrics: {e}")
        return PlainTextResponse(f"# ERROR: Failed to get metrics: {str(e)}")

def run_http_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start de FastMCP HTTP server."""
    logger.info(f"🚀 Starting FastMCP HTTP server on {host}:{port}")
    logger.info("📊 Server biedt zowel MCP tools als HTTP monitoring endpoints")
    logger.info("🔧 Beschikbare MCP tools: process_document_text, process_document_file, classify_document_type, get_metrics, health_check")
    logger.info("🌐 HTTP endpoints: /, /health, /metrics, /metrics/prometheus, /mcp")
    logger.info(f"🔗 MCP endpoint: http://{host}:{port}/mcp/")
    
    try:
        # Start FastMCP server met HTTP transport (volgens FastMCP docs)
        mcp.run(
            transport="http",
            host=host,
            port=port
        )
    except Exception as e:
        logger.error(f"Fout bij starten FastMCP HTTP server: {e}", exc_info=True)
        raise

async def run_http_server_async(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start de FastMCP HTTP server asynchroon."""
    logger.info(f"🚀 Starting FastMCP HTTP server (async) on {host}:{port}")
    logger.info(f"🔗 MCP endpoint: http://{host}:{port}/mcp/")
    
    try:
        # Start FastMCP server asynchroon met HTTP transport (volgens FastMCP docs)
        await mcp.run_async(
            transport="http",
            host=host,
            port=port
        )
    except Exception as e:
        logger.error(f"Fout bij starten FastMCP HTTP server (async): {e}", exc_info=True)
        raise

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments (volgens FastMCP docs: default 127.0.0.1:8000)
    host = "127.0.0.1"
    port = 8000
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    run_http_server(host, port)
