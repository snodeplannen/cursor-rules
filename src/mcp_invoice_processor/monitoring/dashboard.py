"""
Monitoring dashboard voor de MCP Invoice Processor.
Geeft toegang tot metrics, health checks en systeem status.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import json
from typing import Dict, Any

from .metrics import metrics_collector


# FastAPI app initialiseren
app = FastAPI(
    title="MCP Invoice Processor Monitoring",
    description="Monitoring dashboard voor documentverwerking en Ollama integratie",
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


@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Hoofddashboard met overzicht van alle metrics."""
    metrics = metrics_collector.get_comprehensive_metrics()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="nl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MCP Invoice Processor Monitoring</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                text-align: center;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .metric-title {{
                font-size: 18px;
                font-weight: bold;
                color: #333;
                margin-bottom: 15px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 10px;
            }}
            .metric-detail {{
                display: flex;
                justify-content: space-between;
                margin: 5px 0;
                font-size: 14px;
                color: #666;
            }}
            .status-success {{
                color: #28a745;
            }}
            .status-warning {{
                color: #ffc107;
            }}
            .status-error {{
                color: #dc3545;
            }}
            .refresh-btn {{
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-bottom: 20px;
            }}
            .refresh-btn:hover {{
                background: #5a6fd8;
            }}
            .timestamp {{
                text-align: center;
                color: #666;
                font-size: 14px;
                margin-top: 20px;
            }}
        </style>
        <script>
            function refreshMetrics() {{
                location.reload();
            }}
            
            // Auto-refresh elke 30 seconden
            setInterval(refreshMetrics, 30000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 MCP Invoice Processor Monitoring</h1>
                <p>Real-time monitoring van documentverwerking en Ollama integratie</p>
            </div>
            
            <button class="refresh-btn" onclick="refreshMetrics()">🔄 Vernieuwen</button>
            <button id="real-time-btn" class="refresh-btn" style="margin-left: 10px; background: #28a745;" onclick="startRealTimeUpdates()">🔄 Start Real-time</button>
            
            <div class="metrics-grid">
                <!-- Systeem Status -->
                <div class="metric-card">
                    <div class="metric-title">🖥️ Systeem Status</div>
                    <div class="metric-value">{metrics['system']['uptime']}</div>
                    <div class="metric-detail">
                        <span>Memory:</span>
                        <span>{metrics['system']['memory_usage_mb']} MB</span>
                    </div>
                    <div class="metric-detail">
                        <span>CPU:</span>
                        <span>{metrics['system']['cpu_usage_percent']}%</span>
                    </div>
                    <div class="metric-detail">
                        <span>Actieve verbindingen:</span>
                        <span>{metrics['system']['active_connections']}</span>
                    </div>
                </div>
                
                <!-- Document Verwerking -->
                <div class="metric-card">
                    <div class="metric-title">📄 Document Verwerking</div>
                    <div class="metric-value" id="total-docs">{metrics['processing']['total_documents']}</div>
                    <div class="metric-detail">
                        <span>Succesvol:</span>
                        <span class="status-success" id="successful-docs">{metrics['processing']['successful_documents']}</span>
                    </div>
                    <div class="metric-detail">
                        <span>Mislukt:</span>
                        <span class="status-error" id="failed-docs">{metrics['processing']['failed_documents']}</span>
                    </div>
                    <div class="metric-detail">
                        <span>Succes percentage:</span>
                        <span class="status-success" id="success-rate">{metrics['processing']['success_rate_percent']}%</span>
                    </div>
                    <div class="metric-detail">
                        <span>Gemiddelde tijd:</span>
                        <span id="avg-time">{metrics['processing']['average_processing_time']}s</span>
                    </div>
                </div>
                
                <!-- Ollama Integratie -->
                <div class="metric-card">
                    <div class="metric-title">🤖 Ollama Integratie</div>
                    <div class="metric-value" id="total-ollama">{metrics['ollama']['total_requests']}</div>
                    <div class="metric-detail">
                        <span>Succesvol:</span>
                        <span class="status-success" id="successful-ollama">{metrics['ollama']['successful_requests']}</span>
                    </div>
                    <div class="metric-detail">
                        <span>Mislukt:</span>
                        <span class="status-error" id="failed-ollama">{metrics['ollama']['failed_requests']}</span>
                    </div>
                    <div class="metric-detail">
                        <span>Succes percentage:</span>
                        <span class="status-success" id="ollama-success-rate">{metrics['ollama']['success_rate_percent']}%</span>
                    </div>
                    <div class="metric-detail">
                        <span>Gemiddelde tijd:</span>
                        <span id="ollama-avg-time">{metrics['ollama']['average_response_time']}s</span>
                    </div>
                </div>
                
                <!-- Document Types -->
                <div class="metric-card">
                    <div class="metric-title">📋 Document Types</div>
                    <div class="metric-detail">
                        <span>CV's:</span>
                        <span id="cv-count">{metrics['processing']['document_types']['cv']}</span>
                    </div>
                    <div class="metric-detail">
                        <span>Facturen:</span>
                        <span id="invoice-count">{metrics['processing']['document_types']['invoice']}</span>
                    </div>
                    <div class="metric-detail">
                        <span>Onbekend:</span>
                        <span id="unknown-count">{metrics['processing']['document_types']['unknown']}</span>
                    </div>
                </div>
                
                <!-- Performance Metrics -->
                <div class="metric-card">
                    <div class="metric-title">⚡ Performance Metrics</div>
                    <div class="metric-detail">
                        <span>P95 Processing:</span>
                        <span id="p95-processing">{metrics['processing']['p95_processing_time']}s</span>
                    </div>
                    <div class="metric-detail">
                        <span>P99 Processing:</span>
                        <span id="p99-processing">{metrics['processing']['p99_processing_time']}s</span>
                    </div>
                    <div class="metric-detail">
                        <span>P95 Ollama:</span>
                        <span id="p95-ollama">{metrics['ollama']['p95_response_time']}s</span>
                    </div>
                </div>
                
                <!-- Error Breakdown -->
                <div class="metric-card">
                    <div class="metric-title">⚠️ Error Breakdown</div>
                    {''.join([f'<div class="metric-detail"><span>{error_type}:</span><span class="status-error">{count}</span></div>' for error_type, count in metrics['processing']['error_breakdown'].items()])}
                    {''.join([f'<div class="metric-detail"><span>{error_type}:</span><span class="status-error">{count}</span></div>' for error_type, count in metrics['ollama']['error_breakdown'].items()])}
                </div>
            </div>
            
            <div class="timestamp">
                Laatste update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content


@app.get("/health")
async def health_check():
    """Health check endpoint voor monitoring tools."""
    try:
        metrics = metrics_collector.get_comprehensive_metrics()
        
        # Bepaal overall health status
        processing_success_rate = metrics['processing']['success_rate_percent']
        ollama_success_rate = metrics['ollama']['success_rate_percent']
        
        if processing_success_rate >= 95 and ollama_success_rate >= 95:
            status = "healthy"
            status_code = 200
        elif processing_success_rate >= 80 and ollama_success_rate >= 80:
            status = "degraded"
            status_code = 200
        else:
            status = "unhealthy"
            status_code = 503
        
        health_data = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "uptime": metrics['system']['uptime'],
            "processing_success_rate": processing_success_rate,
            "ollama_success_rate": ollama_success_rate,
            "total_documents": metrics['processing']['total_documents'],
            "total_ollama_requests": metrics['ollama']['total_requests']
        }
        
        return JSONResponse(
            content=health_data,
            status_code=status_code
        )
        
    except Exception as e:
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status_code=503
        )


@app.get("/metrics")
async def get_metrics():
    """Haal alle metrics op in JSON formaat."""
    try:
        metrics = metrics_collector.get_comprehensive_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij ophalen van metrics: {e}")


@app.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Haal metrics op in Prometheus formaat."""
    try:
        prometheus_metrics = metrics_collector.export_metrics("prometheus")
        return prometheus_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij exporteren van Prometheus metrics: {e}")


@app.get("/metrics/processing")
async def get_processing_metrics():
    """Haal alleen processing metrics op."""
    try:
        metrics = metrics_collector.get_comprehensive_metrics()
        return JSONResponse(content=metrics['processing'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij ophalen van processing metrics: {e}")


@app.get("/metrics/ollama")
async def get_ollama_metrics():
    """Haal alleen Ollama metrics op."""
    try:
        metrics = metrics_collector.get_comprehensive_metrics()
        return JSONResponse(content=metrics['ollama'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij ophalen van Ollama metrics: {e}")


@app.get("/metrics/system")
async def get_system_metrics():
    """Haal alleen systeem metrics op."""
    try:
        metrics = metrics_collector.get_comprehensive_metrics()
        return JSONResponse(content=metrics['system'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij ophalen van systeem metrics: {e}")


@app.post("/metrics/reset")
async def reset_metrics():
    """Reset alle metrics (alleen voor development/testing)."""
    try:
        # Reset metrics collector
        global metrics_collector
        from .metrics import MetricsCollector
        metrics_collector = MetricsCollector()
        
        return JSONResponse(content={
            "message": "Metrics gereset",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij resetten van metrics: {e}")


def start_dashboard(host: str = "0.0.0.0", port: int = 8000):
    """Start de monitoring dashboard server."""
    print(f"🚀 Monitoring dashboard starten op http://{host}:{port}")
    print(f"📊 Dashboard: http://{host}:{port}/")
    print(f"🔍 Health check: http://{host}:{port}/health")
    print(f"📈 Metrics: http://{host}:{port}/metrics")
    print(f"📊 Prometheus: http://{host}:{port}/metrics/prometheus")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_dashboard()
