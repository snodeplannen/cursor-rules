#!/usr/bin/env python3
"""
Test script voor live metrics sharing tussen MCP server en dashboard.
"""

import sys
import os
import asyncio
from pathlib import Path

# Voeg src directory toe aan Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_live_metrics():
    """Test live metrics sharing."""
    try:
        print("🧪 Test Live Metrics Sharing...")
        
        # Import metrics collector
        from mcp_invoice_processor.monitoring.metrics import metrics_collector, METRICS_FILE
        
        print(f"📁 Metrics bestand: {METRICS_FILE}")
        
        # Simuleer enkele document verwerking events
        print("\n📄 Simuleer document verwerking...")
        metrics_collector.record_document_processing("invoice", True, 2.5)
        metrics_collector.record_document_processing("cv", True, 1.8)
        metrics_collector.record_document_processing("invoice", False, 3.2, "timeout")
        
        # Simuleer Ollama requests
        print("🤖 Simuleer Ollama requests...")
        metrics_collector.record_ollama_request("llama3:8b", 1.5, True)
        metrics_collector.record_ollama_request("llama3:8b", 2.1, True)
        metrics_collector.record_ollama_request("llama3:8b", 3.5, False, "timeout")
        
        # Controleer of bestand is aangemaakt
        if METRICS_FILE.exists():
            print(f"\n✅ Metrics bestand aangemaakt: {METRICS_FILE}")
            
            # Lees bestand
            import json
            with open(METRICS_FILE, 'r') as f:
                metrics = json.load(f)
            
            print("\n📊 Metrics samenvatting:")
            print(f"   - Totaal documenten: {metrics['processing']['total_documents']}")
            print(f"   - Succesvol: {metrics['processing']['successful_documents']}")
            print(f"   - Gefaald: {metrics['processing']['failed_documents']}")
            print(f"   - Succes rate: {metrics['processing']['success_rate_percent']}%")
            print(f"   - Ollama requests: {metrics['ollama']['total_requests']}")
            print(f"   - Ollama succes rate: {metrics['ollama']['success_rate_percent']}%")
            
            print("\n✅ Live metrics sharing werkt!")
            print(f"📡 Start nu het dashboard om live data te zien:")
            print(f"   $env:PYTHONPATH=\"src\"")
            print(f"   python -m mcp_invoice_processor.monitoring.dashboard")
            print(f"   Open: http://localhost:8000")
            
            return True
        else:
            print(f"\n❌ Metrics bestand niet aangemaakt: {METRICS_FILE}")
            return False
        
    except Exception as e:
        print(f"❌ Test gefaald: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_live_metrics())

