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


def generate_demo_metrics():
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
            // Real-time metrics updates
            let updateInterval;
            
            function refreshMetrics() {{
                location.reload();
            }}
            
            async function updateMetricsRealTime() {{
                try {{
                    const response = await fetch('/metrics');
                    const metrics = await response.json();
                    
                    // Update document verwerking metrics
                    document.getElementById('total-docs').textContent = metrics.processing.total_documents;
                    document.getElementById('successful-docs').textContent = metrics.processing.successful_documents;
                    document.getElementById('failed-docs').textContent = metrics.processing.failed_documents;
                    document.getElementById('success-rate').textContent = metrics.processing.success_rate_percent + '%';
                    document.getElementById('avg-time').textContent = metrics.processing.average_processing_time + 's';
                    
                    // Update Ollama metrics
                    document.getElementById('total-ollama').textContent = metrics.ollama.total_requests;
                    document.getElementById('successful-ollama').textContent = metrics.ollama.successful_requests;
                    document.getElementById('failed-ollama').textContent = metrics.ollama.failed_requests;
                    document.getElementById('ollama-success-rate').textContent = metrics.ollama.success_rate_percent + '%';
                    document.getElementById('ollama-avg-time').textContent = metrics.ollama.average_response_time + 's';
                    
                    // Update document types
                    document.getElementById('cv-count').textContent = metrics.processing.document_types.cv;
                    document.getElementById('invoice-count').textContent = metrics.processing.document_types.invoice;
                    document.getElementById('unknown-count').textContent = metrics.processing.document_types.unknown;
                    
                    // Update performance metrics
                    document.getElementById('p95-processing').textContent = metrics.processing.p95_processing_time + 's';
                    document.getElementById('p99-processing').textContent = metrics.processing.p99_processing_time + 's';
                    document.getElementById('p95-ollama').textContent = metrics.ollama.p95_response_time + 's';
                    
                    // Update timestamp
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                    
                }} catch (error) {{
                    console.error('Fout bij ophalen metrics:', error);
                }}
            }}
            
            function startRealTimeUpdates() {{
                // Stop bestaande interval
                if (updateInterval) {{
                    clearInterval(updateInterval);
                }}
                
                // Start real-time updates elke 5 seconden
                updateInterval = setInterval(updateMetricsRealTime, 5000);
                
                // Eerste update direct
                updateMetricsRealTime();
                
                document.getElementById('real-time-btn').textContent = '⏹️ Stop Real-time';
                document.getElementById('real-time-btn').onclick = stopRealTimeUpdates;
            }}
            
            function stopRealTimeUpdates() {{
                if (updateInterval) {{
                    clearInterval(updateInterval);
                    updateInterval = null;
                }}
                
                document.getElementById('real-time-btn').textContent = '🔄 Start Real-time';
                document.getElementById('real-time-btn').onclick = startRealTimeUpdates;
            }}
            
            // Start real-time updates automatisch
            startRealTimeUpdates();
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
                Laatste update: <span id="last-update">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
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
            status_code=500
        )


@app.get("/metrics")
async def get_metrics():
    """JSON endpoint voor metrics data."""
    try:
        metrics = metrics_collector.get_comprehensive_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Prometheus format metrics endpoint."""
    try:
        prometheus_metrics = metrics_collector.export_metrics("prometheus")
        return prometheus_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_dashboard(host: str = "0.0.0.0", port: int = 8000):
    """Start de monitoring dashboard."""
    print("🚀 Starting MCP Invoice Processor Monitoring Dashboard...")
    print(f"🌐 Dashboard beschikbaar op: http://{host}:{port}")
    print(f"📊 Metrics API: http://{host}:{port}/metrics")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    print(f"📈 Prometheus: http://{host}:{port}/metrics/prometheus")
    print("⏹️  Druk Ctrl+C om te stoppen")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_dashboard()
