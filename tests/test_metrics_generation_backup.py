#!/usr/bin/env python3
"""
Test script om de metrics collector bij te werken met test data.
Dit zorgt ervoor dat de monitoring dashboard real-time metrics toont.
"""

import asyncio
import time
import random
from datetime import datetime, timedelta

# Import de metrics collector
from src.mcp_invoice_processor.monitoring.metrics import metrics_collector


def generate_test_metrics():
    """Genereer test metrics om de dashboard te vullen."""
    print("🚀 Starten met genereren van test metrics...")
    
    # Reset metrics voor schone start
    metrics_collector.processing = metrics_collector.processing.__class__()
    metrics_collector.ollama = metrics_collector.ollama.__class__()
    metrics_collector.system = metrics_collector.system.__class__()
    
    print("✅ Metrics gereset")
    
    # Simuleer document verwerking
    print("\n📄 Simuleren document verwerking...")
    
    # CV documenten
    for i in range(5):
        processing_time = random.uniform(1.5, 4.0)
        metrics_collector.record_document_processing("cv", True, processing_time)
        print(f"   CV {i+1} verwerkt in {processing_time:.2f}s")
    
    # Factuur documenten
    for i in range(3):
        processing_time = random.uniform(2.0, 5.0)
        success = random.choice([True, False])
        if success:
            metrics_collector.record_document_processing("invoice", True, processing_time)
            print(f"   Factuur {i+1} succesvol verwerkt in {processing_time:.2f}s")
        else:
            error_type = random.choice(["validation_error", "parsing_error", "timeout"])
            metrics_collector.record_document_processing("invoice", False, processing_time, error_type)
            print(f"   Factuur {i+1} mislukt ({error_type}) na {processing_time:.2f}s")
    
    # Onbekende documenten
    for i in range(2):
        processing_time = random.uniform(0.5, 1.5)
        metrics_collector.record_document_processing("unknown", True, processing_time)
        print(f"   Onbekend document {i+1} verwerkt in {processing_time:.2f}s")
    
    print(f"✅ {metrics_collector.processing.total_documents_processed} documenten verwerkt")
    
    # Simuleer Ollama requests
    print("\n🤖 Simuleren Ollama requests...")
    
    models = ["llama3:8b", "llama3:70b", "mistral:7b"]
    
    for i in range(8):
        model = random.choice(models)
        response_time = random.uniform(0.8, 3.5)
        success = random.choice([True, True, True, False])  # 75% succes rate
        
        if success:
            metrics_collector.record_ollama_request(model, response_time, True)
            print(f"   {model} request {i+1} succesvol in {response_time:.2f}s")
        else:
            error_type = random.choice(["timeout", "model_error", "connection_error"])
            metrics_collector.record_ollama_request(model, response_time, False, error_type)
            print(f"   {model} request {i+1} mislukt ({error_type}) na {response_time:.2f}s")
    
    print(f"✅ {metrics_collector.ollama.total_requests} Ollama requests verwerkt")
    
    # Update systeem metrics
    print("\n🖥️ Bijwerken systeem metrics...")
    
    # Simuleer uptime
    uptime_hours = random.randint(1, 24)
    uptime_minutes = random.randint(0, 59)
    metrics_collector.system.uptime = timedelta(hours=uptime_hours, minutes=uptime_minutes)
    
    # Simuleer memory en CPU usage
    metrics_collector.system.memory_usage_mb = random.uniform(100.0, 800.0)
    metrics_collector.system.cpu_usage_percent = random.uniform(5.0, 45.0)
    
    # Simuleer verbindingen
    metrics_collector.system.active_connections = random.randint(1, 10)
    metrics_collector.system.total_connections = random.randint(10, 100)
    
    print(f"   Uptime: {uptime_hours}h {uptime_minutes}m")
    print(f"   Memory: {metrics_collector.system.memory_usage_mb:.1f} MB")
    print(f"   CPU: {metrics_collector.system.cpu_usage_percent:.1f}%")
    print(f"   Actieve verbindingen: {metrics_collector.system.active_connections}")
    
    print("✅ Systeem metrics bijgewerkt")
    
    # Toon samenvatting
    print("\n📊 Metrics Samenvatting:")
    print("=" * 50)
    
    processing = metrics_collector.processing
    ollama = metrics_collector.ollama
    system = metrics_collector.system
    
    print(f"Documenten: {processing.total_documents_processed} (✅{processing.successful_documents} ❌{processing.failed_documents})")
    print(f"Succes rate: {processing.get_success_rate():.1f}%")
    print(f"Ollama requests: {ollama.total_requests} (✅{ollama.successful_requests} ❌{ollama.failed_requests})")
    print(f"Ollama succes rate: {ollama.get_success_rate():.1f}%")
    print(f"Uptime: {system.get_uptime_formatted()}")
    print(f"Memory: {system.memory_usage_mb:.1f} MB")
    print(f"CPU: {system.cpu_usage_percent:.1f}%")
    
    print("\n🎯 Dashboard is nu gevuld met real-time metrics!")
    print("🌐 Open http://localhost:8000 om de resultaten te zien")


async def continuous_metrics_update():
    """Continu bijwerken van metrics om real-time dashboard te simuleren."""
    print("🔄 Starten met continue metrics updates...")
    print("⏹️  Druk Ctrl+C om te stoppen")
    
    try:
        while True:
            # Voeg wat random metrics toe
            if random.choice([True, False]):  # 50% kans
                doc_type = random.choice(["cv", "invoice", "unknown"])
                processing_time = random.uniform(1.0, 5.0)
                success = random.choice([True, True, True, False])  # 75% succes
                
                if success:
                    metrics_collector.record_document_processing(doc_type, True, processing_time)
                    print(f"📄 {doc_type} document verwerkt in {processing_time:.2f}s")
                else:
                    error_type = random.choice(["validation_error", "timeout", "parsing_error"])
                    metrics_collector.record_document_processing(doc_type, False, processing_time, error_type)
                    print(f"❌ {doc_type} document mislukt ({error_type}) na {processing_time:.2f}s")
            
            if random.choice([True, False]):  # 50% kans
                model = random.choice(["llama3:8b", "llama3:70b", "mistral:7b"])
                response_time = random.uniform(0.5, 4.0)
                success = random.choice([True, True, True, False])  # 75% succes
                
                if success:
                    metrics_collector.record_ollama_request(model, response_time, True)
                    print(f"🤖 {model} request succesvol in {response_time:.2f}s")
                else:
                    error_type = random.choice(["timeout", "model_error"])
                    metrics_collector.record_ollama_request(model, response_time, False, error_type)
                    print(f"❌ {model} request mislukt ({error_type}) na {response_time:.2f}s")
            
            # Update systeem metrics
            metrics_collector.system.memory_usage_mb = random.uniform(100.0, 800.0)
            metrics_collector.system.cpu_usage_percent = random.uniform(5.0, 45.0)
            metrics_collector.system.active_connections = random.randint(1, 15)
            
            # Wacht 5-15 seconden
            wait_time = random.uniform(5, 15)
            print(f"⏳ Wachten {wait_time:.1f}s voor volgende update...")
            await asyncio.sleep(wait_time)
            
    except KeyboardInterrupt:
        print("\n⏹️  Gestopt door gebruiker")


def main():
    """Hoofdfunctie."""
    print("🧪 Test Metrics Generator voor MCP Invoice Processor")
    print("=" * 60)
    
    # Genereer initiële test data
    generate_test_metrics()
    
    print("\n" + "=" * 60)
    print("🎯 Kies een optie:")
    print("1. Eenmalige metrics generatie (al gedaan)")
    print("2. Continue real-time updates (voor live dashboard)")
    print("3. Afsluiten")
    
    try:
        choice = input("\nJouw keuze (1-3): ").strip()
        
        if choice == "2":
            print("\n🚀 Starten met continue updates...")
            asyncio.run(continuous_metrics_update())
        elif choice == "3":
            print("👋 Afsluiten...")
        else:
            print("✅ Eenmalige metrics generatie voltooid!")
            print("🌐 Open http://localhost:8000 om de dashboard te bekijken")
            
    except KeyboardInterrupt:
        print("\n👋 Afsluiten...")


if __name__ == "__main__":
    main()
