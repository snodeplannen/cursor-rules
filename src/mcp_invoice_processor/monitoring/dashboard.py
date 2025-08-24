"""
Monitoring dashboard voor de MCP Invoice Processor.
Geeft toegang tot metrics, health checks en systeem status.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime, timedelta
from .metrics import metrics_collector
import random
from typing import Dict, Any


def generate_demo_metrics() -> None:
    """Genereer demo metrics voor de dashboard."""
    # Reset metrics voor schone start
    metrics_collector.processing = metrics_collector.processing.__class__()
    metrics_collector.ollama = metrics_collector.ollama.__class__()
    metrics_collector.system = metrics_collector.system.__class__()
    
    # Simuleer document verwerking
    for i in range(5):
        processing_time = random.uniform(1.5, 4.0)
        metrics_collector.record_document_processing("cv", True, processing_time)
    
    for i in range(3):
        processing_time = random.uniform(2.0, 5.0)
        success = random.choice([True, False])
        if success:
            metrics_collector.record_document_processing("invoice", True, processing_time)
        else:
            error_type = random.choice(["validation_error", "parsing_error", "timeout"])
            metrics_collector.record_document_processing("invoice", False, processing_time, error_type)
    
    for i in range(2):
        processing_time = random.uniform(0.5, 1.5)
        metrics_collector.record_document_processing("unknown", True, processing_time)
    
    # Simuleer Ollama requests
    models = ["llama3:8b", "llama3:70b", "mistral:7b"]
    for i in range(8):
        model = random.choice(models)
        response_time = random.uniform(0.8, 3.5)
        success = random.choice([True, True, True, False])  # 75% succes rate
        
        if success:
            metrics_collector.record_ollama_request(model, response_time, True)
        else:
            error_type = random.choice(["timeout", "model_error", "connection_error"])
            metrics_collector.record_ollama_request(model, response_time, False, error_type)
    
    # Update systeem metrics
    uptime_hours = random.randint(1, 24)
    uptime_minutes = random.randint(0, 59)
    metrics_collector.system.uptime = timedelta(hours=uptime_hours, minutes=uptime_minutes)
    metrics_collector.system.memory_usage_mb = random.uniform(100.0, 800.0)
    metrics_collector.system.cpu_usage_percent = random.uniform(5.0, 45.0)
    metrics_collector.system.active_connections = random.randint(1, 10)
    metrics_collector.system.total_connections = random.randint(10, 100)
    
    print("✅ Demo metrics gegenereerd voor dashboard")


# Genereer demo metrics bij startup
generate_demo_metrics()


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
async def dashboard_home() -> HTMLResponse:
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
                font-size: 1.1em;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                padding: 30px;
            }}
            .metric-card {{
                background: #f8f9fa;
                border-radius: 10px;
                padding: 25px;
                border-left: 5px solid #3498db;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .metric-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            }}
            .metric-card h3 {{
                margin: 0 0 15px 0;
                color: #2c3e50;
                font-size: 1.3em;
            }}
            .metric-value {{
                font-size: 2em;
                font-weight: bold;
                color: #3498db;
                margin: 10px 0;
            }}
            .metric-label {{
                color: #7f8c8d;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .status-indicator {{
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }}
            .status-healthy {{ background-color: #27ae60; }}
            .status-warning {{ background-color: #f39c12; }}
            .status-error {{ background-color: #e74c3c; }}
            .refresh-btn {{
                background: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 1em;
                transition: background 0.3s;
                margin: 20px;
            }}
            .refresh-btn:hover {{
                background: #2980b9;
            }}
            .chart-container {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .footer {{
                background: #ecf0f1;
                padding: 20px;
                text-align: center;
                color: #7f8c8d;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 MCP Invoice Processor Monitoring</h1>
                <p>Real-time monitoring van documentverwerking en systeem status</p>
                <p>Laatste update: {metrics['timestamp']}</p>
            </div>
            
            <div style="text-align: center;">
                <button class="refresh-btn" onclick="location.reload()">🔄 Vernieuwen</button>
            </div>
            
            <div class="metrics-grid">
                <!-- Systeem Status -->
                <div class="metric-card">
                    <h3>🖥️ Systeem Status</h3>
                    <div class="metric-value">{metrics['system']['uptime']}</div>
                    <div class="metric-label">Uptime</div>
                    <div style="margin-top: 15px;">
                        <div><span class="status-indicator status-healthy"></span>Memory: {metrics['system']['memory_usage_mb']:.1f} MB</div>
                        <div><span class="status-indicator status-healthy"></span>CPU: {metrics['system']['cpu_usage_percent']:.1f}%</div>
                        <div><span class="status-indicator status-healthy"></span>Actieve verbindingen: {metrics['system']['active_connections']}</div>
                    </div>
                </div>
                
                <!-- Document Verwerking -->
                <div class="metric-card">
                    <h3>📄 Document Verwerking</h3>
                    <div class="metric-value">{metrics['processing']['total_documents']}</div>
                    <div class="metric-label">Totaal Verwerkt</div>
                    <div style="margin-top: 15px;">
                        <div>✅ Succesvol: {metrics['processing']['successful_documents']}</div>
                        <div>❌ Gefaald: {metrics['processing']['failed_documents']}</div>
                        <div>📊 Succes Rate: {metrics['processing']['success_rate_percent']:.1f}%</div>
                        <div>⏱️ Gem. tijd: {metrics['processing']['average_processing_time']:.2f}s</div>
                    </div>
                </div>
                
                <!-- Document Types -->
                <div class="metric-card">
                    <h3>📋 Document Types</h3>
                    <div style="margin-top: 15px;">
                        <div>📝 CV's: {metrics['processing']['document_types']['cv']}</div>
                        <div>🧾 Facturen: {metrics['processing']['document_types']['invoice']}</div>
                        <div>❓ Onbekend: {metrics['processing']['document_types']['unknown']}</div>
                    </div>
                </div>
                
                <!-- Ollama Integratie -->
                <div class="metric-card">
                    <h3>🤖 Ollama Integratie</h3>
                    <div class="metric-value">{metrics['ollama']['total_requests']}</div>
                    <div class="metric-label">Totaal Requests</div>
                    <div style="margin-top: 15px;">
                        <div>✅ Succesvol: {metrics['ollama']['successful_requests']}</div>
                        <div>❌ Gefaald: {metrics['ollama']['failed_requests']}</div>
                        <div>📊 Succes Rate: {metrics['ollama']['success_rate_percent']:.1f}%</div>
                        <div>⏱️ Gem. response: {metrics['ollama']['average_response_time']:.2f}s</div>
                    </div>
                </div>
                
                <!-- Performance Metrics -->
                <div class="metric-card">
                    <h3>⚡ Performance</h3>
                    <div style="margin-top: 15px;">
                        <div>📈 P95 Processing: {metrics['processing']['p95_processing_time']:.2f}s</div>
                        <div>📈 P99 Processing: {metrics['processing']['p99_processing_time']:.2f}s</div>
                        <div>📈 P95 Response: {metrics['ollama']['p95_response_time']:.2f}s</div>
                    </div>
                </div>
                
                <!-- Error Breakdown -->
                <div class="metric-card">
                    <h3>🚨 Error Breakdown</h3>
                    <div style="margin-top: 15px;">
                        <div style="color: #e74c3c; font-weight: bold;">Processing Errors:</div>
                        {''.join([f'<div>• {error}: {count}</div>' for error, count in metrics['processing']['error_breakdown'].items()])}
                        <div style="margin-top: 10px; color: #e74c3c; font-weight: bold;">Ollama Errors:</div>
                        {''.join([f'<div>• {error}: {count}</div>' for error, count in metrics['ollama']['error_breakdown'].items()])}
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>MCP Invoice Processor v1.0.0 | Monitoring Dashboard</p>
                <p>Gegenereerd op {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
        
        <script>
            // Auto-refresh elke 30 seconden
            setInterval(() => {{
                location.reload();
            }}, 30000);
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@app.get("/metrics", response_class=JSONResponse)
async def get_metrics() -> JSONResponse:
    """API endpoint voor het ophalen van alle metrics in JSON formaat."""
    try:
        metrics = metrics_collector.get_comprehensive_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij ophalen metrics: {str(e)}")


@app.get("/metrics/prometheus")
async def get_prometheus_metrics() -> str:
    """API endpoint voor Prometheus metrics."""
    try:
        return metrics_collector.export_metrics("prometheus")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij exporteren Prometheus metrics: {str(e)}")


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    try:
        # Basis health check
        uptime = metrics_collector.system.uptime.total_seconds()
        memory_usage = metrics_collector.system.memory_usage_mb
        cpu_usage = metrics_collector.system.cpu_usage_percent
        
        # Bepaal status
        status = "healthy"
        if uptime < 60:  # Minder dan 1 minuut uptime
            status = "starting"
        elif memory_usage > 1000:  # Meer dan 1GB memory
            status = "warning"
        elif cpu_usage > 80:  # Meer dan 80% CPU
            status = "warning"
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime,
            "memory_usage_mb": memory_usage,
            "cpu_usage_percent": cpu_usage,
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "version": "1.0.0"
        }


@app.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Gedetailleerde health check met alle componenten."""
    try:
        # Component health checks
        components: Dict[str, Dict[str, Any]] = {
            "system": {
                "status": "healthy",
                "uptime": metrics_collector.system.get_uptime_formatted(),
                "memory_usage_mb": metrics_collector.system.memory_usage_mb,
                "cpu_usage_percent": metrics_collector.system.cpu_usage_percent
            },
            "processing": {
                "status": "healthy" if metrics_collector.processing.total_documents_processed > 0 else "no_data",
                "total_documents": metrics_collector.processing.total_documents_processed,
                "success_rate": metrics_collector.processing.get_success_rate()
            },
            "ollama": {
                "status": "healthy" if metrics_collector.ollama.total_requests > 0 else "no_data",
                "total_requests": metrics_collector.ollama.total_requests,
                "success_rate": metrics_collector.ollama.get_success_rate()
            }
        }
        
        # Overall status
        overall_status = "healthy"
        component_values = list(components.values())
        if any(comp["status"] == "error" for comp in component_values):
            overall_status = "error"
        elif any(comp["status"] == "warning" for comp in component_values):
            overall_status = "warning"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": components,
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "version": "1.0.0"
        }


@app.post("/demo/reset")
async def reset_demo_metrics() -> Dict[str, str]:
    """Reset demo metrics en genereer nieuwe."""
    try:
        generate_demo_metrics()
        return {"message": "Demo metrics gereset en nieuwe gegenereerd"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij resetten demo metrics: {str(e)}")


@app.get("/demo/status")
async def get_demo_status() -> Dict[str, Any]:
    """Status van demo metrics."""
    return {
        "demo_active": True,
        "last_generated": datetime.now().isoformat(),
        "note": "Demo metrics worden automatisch gegenereerd bij startup en kunnen handmatig gereset worden"
    }


if __name__ == "__main__":
    print("🚀 Starting MCP Invoice Processor Monitoring Dashboard...")
    print("📊 Dashboard beschikbaar op: http://localhost:8000")
    print("🔍 API endpoints:")
    print("   - GET  /metrics - JSON metrics")
    print("   - GET  /metrics/prometheus - Prometheus format")
    print("   - GET  /health - Health check")
    print("   - GET  /health/detailed - Gedetailleerde health check")
    print("   - POST /demo/reset - Reset demo metrics")
    print("   - GET  /demo/status - Demo status")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
