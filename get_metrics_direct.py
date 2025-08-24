#!/usr/bin/env python3
"""
Direct script om metrics op te halen van de MCP Invoice Processor.
"""
import sys
import os

# Voeg src directory toe aan Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.mcp_invoice_processor.monitoring.metrics import metrics_collector

def main():
    """Haal alle metrics op en toon ze."""
    print("📊 MCP Invoice Processor Metrics")
    print("=" * 50)
    
    try:
        # Haal comprehensive metrics op
        metrics = metrics_collector.get_comprehensive_metrics()
        
        # Systeem metrics
        print("\n🖥️  Systeem Status:")
        print(f"   Uptime: {metrics['system']['uptime']}")
        print(f"   Memory: {metrics['system']['memory_usage_mb']:.1f} MB")
        print(f"   CPU: {metrics['system']['cpu_usage_percent']:.1f}%")
        print(f"   Actieve verbindingen: {metrics['system']['active_connections']}")
        
        # Document verwerking metrics
        print("\n📄 Document Verwerking:")
        print(f"   Totaal verwerkt: {metrics['processing']['total_documents']}")
        print(f"   Succesvol: {metrics['processing']['successful_documents']}")
        print(f"   Mislukt: {metrics['processing']['failed_documents']}")
        print(f"   Succes percentage: {metrics['processing']['success_rate_percent']:.1f}%")
        print(f"   Gemiddelde tijd: {metrics['processing']['average_processing_time']:.3f}s")
        print(f"   P95 tijd: {metrics['processing']['p95_processing_time']:.3f}s")
        
        # Document types breakdown
        print(f"   CV's: {metrics['processing']['document_types']['cv']}")
        print(f"   Facturen: {metrics['processing']['document_types']['invoice']}")
        print(f"   Onbekend: {metrics['processing']['document_types']['unknown']}")
        
        # Ollama metrics
        print("\n🤖 Ollama Integratie:")
        print(f"   Totaal requests: {metrics['ollama']['total_requests']}")
        print(f"   Succesvol: {metrics['ollama']['successful_requests']}")
        print(f"   Mislukt: {metrics['ollama']['failed_requests']}")
        print(f"   Succes percentage: {metrics['ollama']['success_rate_percent']:.1f}%")
        print(f"   Gemiddelde response tijd: {metrics['ollama']['average_response_time']:.3f}s")
        print(f"   P95 response tijd: {metrics['ollama']['p95_response_time']:.3f}s")
        
        # Model usage
        if metrics['ollama']['model_usage']:
            print("\n📈 Model Gebruik:")
            for model, count in metrics['ollama']['model_usage'].items():
                print(f"   {model}: {count} requests")
        
        # Error breakdown
        if metrics['processing']['error_breakdown']:
            print("\n⚠️  Verwerking Fouten:")
            for error_type, count in metrics['processing']['error_breakdown'].items():
                print(f"   {error_type}: {count}")
        
        if metrics['ollama']['error_breakdown']:
            print("\n⚠️  Ollama Fouten:")
            for error_type, count in metrics['ollama']['error_breakdown'].items():
                print(f"   {error_type}: {count}")
        
        print(f"\n🕐 Laatste update: {metrics['timestamp']}")
        
    except Exception as e:
        print(f"❌ Fout bij ophalen metrics: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
