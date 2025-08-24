#!/usr/bin/env python3
"""
HTTP Server wrapper voor de MCP Invoice Processor.
Maakt de MCP functionaliteit beschikbaar via HTTP endpoints.
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .monitoring.metrics import metrics_collector

# Configureer logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Maak FastAPI app
app = FastAPI(
    title="MCP Invoice Processor HTTP Server",
    description="HTTP wrapper voor MCP Invoice Processor functionaliteit",
    version="1.0.0"
)

# CORS middleware toevoegen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint met server informatie."""
    return {
        "name": "MCP Invoice Processor HTTP Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "metrics_prometheus": "/metrics/prometheus"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        return {
            "status": "healthy",
            "service": "MCP Invoice Processor HTTP Server",
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.get("/metrics")
async def get_metrics():
    """Haal alle metrics op in JSON formaat."""
    try:
        metrics = metrics_collector.get_comprehensive_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@app.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Haal metrics op in Prometheus formaat."""
    try:
        prometheus_metrics = metrics_collector.get_prometheus_metrics()
        return PlainTextResponse(content=prometheus_metrics)
    except Exception as e:
        logger.error(f"Failed to get Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Prometheus metrics: {str(e)}")

def run_http_server(host: str = "0.0.0.0", port: int = 8080):
    """Start de HTTP server."""
    logger.info(f"Starting HTTP server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    host = "0.0.0.0"
    port = 8080
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    run_http_server(host, port)
