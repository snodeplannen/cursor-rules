"""
Metrics collector voor de MCP Invoice Processor.
Verzamelt performance en usage statistieken.
"""
import time
from typing import Dict, Optional, Any, Deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Metrics bestand voor sharing tussen processen
METRICS_FILE = Path("logs/metrics_live.json")


@dataclass
class ProcessingMetrics:
    """Metrics voor documentverwerking."""
    total_documents_processed: int = 0
    successful_documents: int = 0
    failed_documents: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    
    # Per documenttype
    cv_documents: int = 0
    invoice_documents: int = 0
    unknown_documents: int = 0
    
    # Error tracking
    error_counts: Dict[str, int] = field(default_factory=dict)
    
    # Performance tracking
    processing_times: Deque[float] = field(default_factory=lambda: deque(maxlen=100))
    
    def update_processing_time(self, processing_time: float) -> None:
        """Update processing time metrics."""
        self.total_processing_time += processing_time
        self.processing_times.append(processing_time)
        self.average_processing_time = self.total_processing_time / self.total_documents_processed
    
    def record_success(self, doc_type: str, processing_time: float) -> None:
        """Record successful document processing."""
        self.total_documents_processed += 1
        self.successful_documents += 1
        self.update_processing_time(processing_time)
        
        if doc_type == "cv":
            self.cv_documents += 1
        elif doc_type == "invoice":
            self.invoice_documents += 1
        else:
            self.unknown_documents += 1
    
    def record_failure(self, doc_type: str, error_type: str, processing_time: float) -> None:
        """Record failed document processing."""
        self.total_documents_processed += 1
        self.failed_documents += 1
        self.update_processing_time(processing_time)
        
        if doc_type == "cv":
            self.cv_documents += 1
        elif doc_type == "invoice":
            self.invoice_documents += 1
        else:
            self.unknown_documents += 1
        
        # Track error types
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_documents_processed == 0:
            return 0.0
        return (self.successful_documents / self.total_documents_processed) * 100
    
    def get_percentile_processing_time(self, percentile: float) -> float:
        """Get processing time for a specific percentile."""
        if not self.processing_times:
            return 0.0
        
        sorted_times = sorted(self.processing_times)
        index = int(len(sorted_times) * percentile / 100)
        return sorted_times[index]


@dataclass
class OllamaMetrics:
    """Metrics voor Ollama integratie."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    average_response_time: float = 0.0
    
    # Response time tracking
    response_times: Deque[float] = field(default_factory=lambda: deque(maxlen=100))
    
    # Model usage tracking
    model_usage: Dict[str, int] = field(default_factory=dict)
    
    # Error tracking
    error_counts: Dict[str, int] = field(default_factory=dict)
    
    def record_request(self, model: str, response_time: float, success: bool, error_type: Optional[str] = None) -> None:
        """Record Ollama request metrics."""
        self.total_requests += 1
        self.total_response_time += response_time
        self.response_times.append(response_time)
        self.average_response_time = self.total_response_time / self.total_requests
        
        # Track model usage
        self.model_usage[model] = self.model_usage.get(model, 0) + 1
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error_type:
                self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_percentile_response_time(self, percentile: float) -> float:
        """Get response time for a specific percentile."""
        if not self.response_times:
            return 0.0
        
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * percentile / 100)
        return sorted_times[index]


@dataclass
class SystemMetrics:
    """System-level metrics."""
    start_time: datetime = field(default_factory=datetime.now)
    uptime: timedelta = field(default_factory=lambda: timedelta(0))
    
    # Memory usage (simulated for now)
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # Active connections
    active_connections: int = 0
    total_connections: int = 0
    
    def update_uptime(self) -> None:
        """Update uptime."""
        self.uptime = datetime.now() - self.start_time
    
    def get_uptime_formatted(self) -> str:
        """Get formatted uptime string."""
        total_seconds = int(self.uptime.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class MetricsCollector:
    """Hoofdklasse voor het verzamelen en beheren van alle metrics."""
    
    def __init__(self) -> None:
        self.processing = ProcessingMetrics()
        self.ollama = OllamaMetrics()
        self.system = SystemMetrics()
        
        # Performance tracking
        self._start_times: Dict[str, float] = {}
        
        # Historical data for trends
        self._hourly_metrics: Deque[Dict[str, Any]] = field(default_factory=lambda: deque(maxlen=24))
        
        logger.info("Metrics collector geïnitialiseerd")
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self._start_times[operation] = time.time()
    
    def stop_timer(self, operation: str) -> float:
        """Stop timing an operation and return duration."""
        if operation not in self._start_times:
            return 0.0
        
        duration = time.time() - self._start_times[operation]
        del self._start_times[operation]
        return duration
    
    def record_document_processing(self, doc_type: str, success: bool, processing_time: float, error_type: Optional[str] = None) -> None:
        """Record document processing metrics."""
        if success:
            self.processing.record_success(doc_type, processing_time)
        else:
            self.processing.record_failure(doc_type, error_type or "unknown", processing_time)
        
        logger.debug(f"Document processing recorded: {doc_type}, success: {success}, time: {processing_time:.2f}s")
        
        # Schrijf metrics naar bestand voor live sharing
        self._save_metrics_to_file()
    
    def record_ollama_request(self, model: str, response_time: float, success: bool, error_type: Optional[str] = None) -> None:
        """Record Ollama request metrics."""
        self.ollama.record_request(model, response_time, success, error_type)
        
        logger.debug(f"Ollama request recorded: {model}, success: {success}, time: {response_time:.2f}s")
        
        # Schrijf metrics naar bestand voor live sharing
        self._save_metrics_to_file()
    
    def update_system_metrics(self) -> None:
        """Update system metrics."""
        self.system.update_uptime()
        # In een echte implementatie zouden we hier system calls maken
        # Voor nu simuleren we deze waarden
        import random
        self.system.memory_usage_mb = 150.0 + random.uniform(-10, 10)
        self.system.cpu_usage_percent = 25.0 + random.uniform(-5, 5)
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics overview."""
        self.update_system_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "uptime": self.system.get_uptime_formatted(),
                "memory_usage_mb": round(self.system.memory_usage_mb, 2),
                "cpu_usage_percent": round(self.system.cpu_usage_percent, 2),
                "active_connections": self.system.active_connections,
                "total_connections": self.system.total_connections
            },
            "processing": {
                "total_documents": self.processing.total_documents_processed,
                "successful_documents": self.processing.successful_documents,
                "failed_documents": self.processing.failed_documents,
                "success_rate_percent": round(self.processing.get_success_rate(), 2),
                "average_processing_time": round(self.processing.average_processing_time, 3),
                "p95_processing_time": round(self.processing.get_percentile_processing_time(95), 3),
                "p99_processing_time": round(self.processing.get_percentile_processing_time(99), 3),
                "document_types": {
                    "cv": self.processing.cv_documents,
                    "invoice": self.processing.invoice_documents,
                    "unknown": self.processing.unknown_documents
                },
                "error_breakdown": self.processing.error_counts
            },
            "ollama": {
                "total_requests": self.ollama.total_requests,
                "successful_requests": self.ollama.successful_requests,
                "failed_requests": self.ollama.failed_requests,
                "success_rate_percent": round(self.ollama.get_success_rate(), 2),
                "average_response_time": round(self.ollama.average_response_time, 3),
                "p95_response_time": round(self.ollama.get_percentile_response_time(95), 3),
                "model_usage": self.ollama.model_usage,
                "error_breakdown": self.ollama.error_counts
            }
        }
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        metrics = self.get_comprehensive_metrics()
        
        if format.lower() == "json":
            return json.dumps(metrics, indent=2, default=str)
        elif format.lower() == "prometheus":
            return self._to_prometheus_format(metrics)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _to_prometheus_format(self, metrics: Dict[str, Any]) -> str:
        """Convert metrics to Prometheus format."""
        lines = []
        
        # System metrics
        lines.append("# HELP mcp_uptime_seconds System uptime in seconds")
        lines.append("# TYPE mcp_uptime_seconds gauge")
        lines.append(f"mcp_uptime_seconds {self.system.uptime.total_seconds()}")
        
        lines.append("# HELP mcp_memory_usage_mb Memory usage in MB")
        lines.append("# TYPE mcp_memory_usage_mb gauge")
        lines.append(f"mcp_memory_usage_mb {self.system.memory_usage_mb}")
        
        lines.append("# HELP mcp_cpu_usage_percent CPU usage percentage")
        lines.append("# TYPE mcp_cpu_usage_percent gauge")
        lines.append(f"mcp_cpu_usage_percent {self.system.cpu_usage_percent}")
        
        # Processing metrics
        lines.append("# HELP mcp_documents_total Total documents processed")
        lines.append("# TYPE mcp_documents_total counter")
        lines.append(f"mcp_documents_total {self.processing.total_documents_processed}")
        
        lines.append("# HELP mcp_documents_successful Successful documents processed")
        lines.append("# TYPE mcp_documents_successful counter")
        lines.append(f"mcp_documents_successful {self.processing.successful_documents}")
        
        lines.append("# HELP mcp_documents_failed Failed documents processed")
        lines.append("# TYPE mcp_documents_failed counter")
        lines.append(f"mcp_documents_failed {self.processing.failed_documents}")
        
        lines.append("# HELP mcp_processing_time_seconds Document processing time")
        lines.append("# TYPE mcp_processing_time_seconds histogram")
        lines.append("mcp_processing_time_seconds_bucket{le=\"0.1\"} " + str(len([t for t in self.processing.processing_times if t <= 0.1])))
        lines.append("mcp_processing_time_seconds_bucket{le=\"0.5\"} " + str(len([t for t in self.processing.processing_times if t <= 0.5])))
        lines.append("mcp_processing_time_seconds_bucket{le=\"1.0\"} " + str(len([t for t in self.processing.processing_times if t <= 1.0])))
        lines.append("mcp_processing_time_seconds_bucket{le=\"5.0\"} " + str(len([t for t in self.processing.processing_times if t <= 5.0])))
        lines.append("mcp_processing_time_seconds_bucket{le=\"+Inf\"} " + str(len(self.processing.processing_times)))
        
        # Ollama metrics
        lines.append("# HELP mcp_ollama_requests_total Total Ollama requests")
        lines.append("# TYPE mcp_ollama_requests_total counter")
        lines.append(f"mcp_ollama_requests_total {self.ollama.total_requests}")
        
        lines.append("# HELP mcp_ollama_response_time_seconds Ollama response time")
        lines.append("# TYPE mcp_ollama_response_time_seconds histogram")
        lines.append("mcp_ollama_response_time_seconds_bucket{le=\"1.0\"} " + str(len([t for t in self.ollama.response_times if t <= 1.0])))
        lines.append("mcp_ollama_response_time_seconds_bucket{le=\"5.0\"} " + str(len([t for t in self.ollama.response_times if t <= 5.0])))
        lines.append("mcp_ollama_response_time_seconds_bucket{le=\"10.0\"} " + str(len([t for t in self.ollama.response_times if t <= 10.0])))
        lines.append("mcp_ollama_response_time_seconds_bucket{le=\"30.0\"} " + str(len([t for t in self.ollama.response_times if t <= 30.0])))
        lines.append("mcp_ollama_response_time_seconds_bucket{le=\"+Inf\"} " + str(len(self.ollama.response_times)))
        
        return "\n".join(lines)
    
    def _save_metrics_to_file(self) -> None:
        """Sla metrics op naar bestand voor live sharing tussen processen."""
        try:
            # Zorg dat logs directory bestaat
            METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            # Haal metrics op en schrijf naar bestand
            metrics = self.get_comprehensive_metrics()
            with open(METRICS_FILE, 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Fout bij opslaan metrics naar bestand: {e}")
    
    @staticmethod
    def load_metrics_from_file() -> Optional[Dict[str, Any]]:
        """Laad metrics uit bestand voor live sharing tussen processen."""
        try:
            if METRICS_FILE.exists():
                with open(METRICS_FILE, 'r') as f:
                    parsed_data: Dict[str, Any] = json.load(f)
                    return parsed_data
            return None
        except Exception as e:
            logger.error(f"Fout bij laden metrics uit bestand: {e}")
            return None


# Global metrics collector instance
metrics_collector = MetricsCollector()
