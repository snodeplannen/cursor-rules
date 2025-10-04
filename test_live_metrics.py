#!/usr/bin/env python3
"""
Test live metrics generation met v2.0 processors.
"""

import asyncio
import time
from typing import Dict, Any

from mcp_invoice_processor.monitoring.metrics import metrics_collector
from mcp_invoice_processor.processors import get_registry


async def generate_test_metrics() -> None:
    """Genereer test metrics voor dashboard met v2.0."""
    print("🔄 Genereren test metrics...")
    
    registry = get_registry()
    
    # Simuleer document processing
    for i in range(10):
        doc_type = "invoice" if i % 2 == 0 else "cv"
        success = i % 3 != 0  # 2/3 success rate
        processing_time = 1.5 + (i * 0.3)
        
        metrics_collector.record_document_processing(
            doc_type=doc_type,
            success=success,
            processing_time=processing_time,
            error_type=None if success else "test_error"
        )
        
        # Processor statistics
        processor = registry.get_processor(doc_type)
        if processor:
            processor.update_statistics(
                success=success,
                processing_time=processing_time,
                confidence=85.0 + i,
                completeness=90.0 if success else 50.0
            )
    
    # Simuleer Ollama requests
    for i in range(15):
        metrics_collector.record_ollama_request(
            model="llama3.2",
            response_time=1.2 + (i * 0.2),
            success=i % 4 != 0,  # 3/4 success rate
            error_type=None if i % 4 != 0 else "timeout"
        )
    
    # Print metrics
    metrics = metrics_collector.get_comprehensive_metrics()
    processor_stats = registry.get_all_statistics()
    
    print(f"\n📊 Metrics gegenereerd:")
    print(f"   Documents: {metrics['processing']['total_documents']}")
    print(f"   Ollama requests: {metrics['ollama']['total_requests']}")
    print(f"   Processors: {processor_stats['total_processors']}")
    print(f"   Global success rate: {processor_stats['global']['global_success_rate']:.1f}%")
    
    print("\n✅ Test metrics klaar!")


if __name__ == "__main__":
    asyncio.run(generate_test_metrics())
