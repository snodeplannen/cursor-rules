"""
Tests voor monitoring en metrics functionaliteit.
"""
import pytest
import time
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.mcp_invoice_processor.monitoring.metrics import (
    MetricsCollector, ProcessingMetrics, OllamaMetrics, SystemMetrics
)


class TestProcessingMetrics:
    """Test ProcessingMetrics class."""
    
    def test_initial_state(self):
        """Test initiële staat van ProcessingMetrics."""
        print("\n🧪 Test: ProcessingMetrics initial state")
        print("Input: Nieuwe ProcessingMetrics instantie")
        print("Expected: Alle tellers op 0, lege error_counts")
        
        metrics = ProcessingMetrics()
        
        # Test alle velden
        actual_total = metrics.total_documents_processed
        actual_successful = metrics.successful_documents
        actual_failed = metrics.failed_documents
        actual_avg_time = metrics.average_processing_time
        actual_cv = metrics.cv_documents
        actual_invoice = metrics.invoice_documents
        actual_unknown = metrics.unknown_documents
        actual_errors = metrics.error_counts
        
        print(f"Actual total_documents: {actual_total}")
        print(f"Actual successful: {actual_successful}")
        print(f"Actual failed: {actual_failed}")
        print(f"Actual avg_time: {actual_avg_time}")
        print(f"Actual cv: {actual_cv}")
        print(f"Actual invoice: {actual_invoice}")
        print(f"Actual unknown: {actual_unknown}")
        print(f"Actual errors: {actual_errors}")
        
        assert actual_total == 0, f"Expected 0, got {actual_total}"
        assert actual_successful == 0, f"Expected 0, got {actual_successful}"
        assert actual_failed == 0, f"Expected 0, got {actual_failed}"
        assert actual_avg_time == 0.0, f"Expected 0.0, got {actual_avg_time}"
        assert actual_cv == 0, f"Expected 0, got {actual_cv}"
        assert actual_invoice == 0, f"Expected 0, got {actual_invoice}"
        assert actual_unknown == 0, f"Expected 0, got {actual_unknown}"
        assert actual_errors == {}, f"Expected empty dict, got {actual_errors}"
        
        print("✅ Test passed: Alle initial values correct")
    
    def test_record_success_cv(self):
        """Test succesvolle CV verwerking recording."""
        print("\n🧪 Test: Record successful CV processing")
        print("Input: CV document met processing_time=2.5s")
        print("Expected: total=1, successful=1, cv=1, avg_time=2.5")
        
        metrics = ProcessingMetrics()
        processing_time = 2.5
        
        metrics.record_success("cv", processing_time)
        
        actual_total = metrics.total_documents_processed
        actual_successful = metrics.successful_documents
        actual_failed = metrics.failed_documents
        actual_cv = metrics.cv_documents
        actual_invoice = metrics.invoice_documents
        actual_unknown = metrics.unknown_documents
        actual_avg_time = metrics.average_processing_time
        
        print(f"Actual total: {actual_total}")
        print(f"Actual successful: {actual_successful}")
        print(f"Actual failed: {actual_failed}")
        print(f"Actual cv: {actual_cv}")
        print(f"Actual invoice: {actual_invoice}")
        print(f"Actual unknown: {actual_unknown}")
        print(f"Actual avg_time: {actual_avg_time}")
        
        assert actual_total == 1, f"Expected 1, got {actual_total}"
        assert actual_successful == 1, f"Expected 1, got {actual_successful}"
        assert actual_failed == 0, f"Expected 0, got {actual_failed}"
        assert actual_cv == 1, f"Expected 1, got {actual_cv}"
        assert actual_invoice == 0, f"Expected 0, got {actual_invoice}"
        assert actual_unknown == 0, f"Expected 0, got {actual_unknown}"
        assert actual_avg_time == 2.5, f"Expected 2.5, got {actual_avg_time}"
        
        print("✅ Test passed: CV success recording correct")
    
    def test_record_success_invoice(self):
        """Test succesvolle factuur verwerking recording."""
        print("\n🧪 Test: Record successful invoice processing")
        print("Input: Invoice document met processing_time=1.8s")
        print("Expected: total=1, successful=1, invoice=1, avg_time=1.8")
        
        metrics = ProcessingMetrics()
        processing_time = 1.8
        
        metrics.record_success("invoice", processing_time)
        
        actual_total = metrics.total_documents_processed
        actual_successful = metrics.successful_documents
        actual_failed = metrics.failed_documents
        actual_cv = metrics.cv_documents
        actual_invoice = metrics.invoice_documents
        actual_unknown = metrics.unknown_documents
        actual_avg_time = metrics.average_processing_time
        
        print(f"Actual total: {actual_total}")
        print(f"Actual successful: {actual_successful}")
        print(f"Actual failed: {actual_failed}")
        print(f"Actual cv: {actual_cv}")
        print(f"Actual invoice: {actual_invoice}")
        print(f"Actual unknown: {actual_unknown}")
        print(f"Actual avg_time: {actual_avg_time}")
        
        assert actual_total == 1, f"Expected 1, got {actual_total}"
        assert actual_successful == 1, f"Expected 1, got {actual_successful}"
        assert actual_failed == 0, f"Expected 0, got {actual_failed}"
        assert actual_cv == 0, f"Expected 0, got {actual_cv}"
        assert actual_invoice == 1, f"Expected 1, got {actual_invoice}"
        assert actual_unknown == 0, f"Expected 0, got {actual_unknown}"
        assert actual_avg_time == 1.8, f"Expected 1.8, got {actual_avg_time}"
        
        print("✅ Test passed: Invoice success recording correct")
    
    def test_record_failure(self):
        """Test mislukte verwerking recording."""
        print("\n🧪 Test: Record failed processing")
        print("Input: CV document met error='validation_error' en processing_time=3.2s")
        print("Expected: total=1, failed=1, cv=1, error_counts['validation_error']=1")
        
        metrics = ProcessingMetrics()
        processing_time = 3.2
        
        metrics.record_failure("cv", "validation_error", processing_time)
        
        actual_total = metrics.total_documents_processed
        actual_successful = metrics.successful_documents
        actual_failed = metrics.failed_documents
        actual_cv = metrics.cv_documents
        actual_error_count = metrics.error_counts.get("validation_error", 0)
        
        print(f"Actual total: {actual_total}")
        print(f"Actual successful: {actual_successful}")
        print(f"Actual failed: {actual_failed}")
        print(f"Actual cv: {actual_cv}")
        print(f"Actual validation_error count: {actual_error_count}")
        
        assert actual_total == 1, f"Expected 1, got {actual_total}"
        assert actual_successful == 0, f"Expected 0, got {actual_successful}"
        assert actual_failed == 1, f"Expected 1, got {actual_failed}"
        assert actual_cv == 1, f"Expected 1, got {actual_cv}"
        assert actual_error_count == 1, f"Expected 1, got {actual_error_count}"
        
        print("✅ Test passed: Failure recording correct")
    
    def test_success_rate_calculation(self):
        """Test succes percentage berekening."""
        print("\n🧪 Test: Success rate calculation")
        print("Input: 0 documenten, dan 2 succesvol + 1 mislukt")
        print("Expected: 0% voor 0 documenten, 66.67% voor 3 documenten")
        
        metrics = ProcessingMetrics()
        
        # Test 0 documenten
        expected_rate_0 = 0.0
        actual_rate_0 = metrics.get_success_rate()
        print(f"0 documenten - Expected: {expected_rate_0}%, Actual: {actual_rate_0}%")
        assert actual_rate_0 == expected_rate_0, f"Expected {expected_rate_0}%, got {actual_rate_0}%"
        
        # Test 2 succesvol, 1 mislukt
        metrics.record_success("cv", 1.0)
        metrics.record_success("invoice", 1.5)
        metrics.record_failure("cv", "error", 2.0)
        
        expected_rate_3 = 66.67
        actual_rate_3 = metrics.get_success_rate()
        print(f"3 documenten (2 succesvol, 1 mislukt) - Expected: {expected_rate_3}%, Actual: {actual_rate_3}%")
        
        tolerance = 0.01
        assert abs(actual_rate_3 - expected_rate_3) < tolerance, f"Expected {expected_rate_3}%, got {actual_rate_3}% (tolerance: {tolerance})"
        
        print("✅ Test passed: Success rate calculation correct")
    
    def test_percentile_calculation(self):
        """Test percentile berekening."""
        print("\n🧪 Test: Percentile calculation")
        print("Input: Processing times [1.0, 2.0, 3.0, 4.0, 5.0]")
        print("Expected: P50=3.0, P90=5.0, P95=5.0")
        
        metrics = ProcessingMetrics()

        # Voeg wat processing times toe
        test_times = [1.0, 2.0, 3.0, 4.0, 5.0]
        for time in test_times:
            metrics.record_success("cv", time)
        
        print(f"Added processing times: {test_times}")
        
        # Test P50 (median)
        expected_p50 = 3.0
        actual_p50 = metrics.get_percentile_processing_time(50)
        print(f"P50 (median) - Expected: {expected_p50}, Actual: {actual_p50}")
        assert actual_p50 == expected_p50, f"Expected P50={expected_p50}, got {actual_p50}"
        
        # Test P90
        expected_p90 = 5.0
        actual_p90 = metrics.get_percentile_processing_time(90)
        print(f"P90 - Expected: {expected_p90}, Actual: {actual_p90}")
        assert actual_p90 == expected_p90, f"Expected P90={expected_p90}, got {actual_p90}"
        
        # Test P95
        expected_p95 = 5.0
        actual_p95 = metrics.get_percentile_processing_time(95)
        print(f"P95 - Expected: {expected_p95}, Actual: {actual_p95}")
        assert actual_p95 == expected_p95, f"Expected P95={expected_p95}, got {actual_p95}"
        
        print("✅ Test passed: Percentile calculation correct")


class TestOllamaMetrics:
    """Test OllamaMetrics class."""
    
    def test_initial_state(self):
        """Test initiële staat van OllamaMetrics."""
        print("\n🧪 Test: OllamaMetrics initial state")
        print("Input: Nieuwe OllamaMetrics instantie")
        print("Expected: Alle tellers op 0, lege dicts")
        
        metrics = OllamaMetrics()

        actual_total = metrics.total_requests
        actual_successful = metrics.successful_requests
        actual_failed = metrics.failed_requests
        actual_avg_time = metrics.average_response_time
        actual_models = metrics.model_usage
        actual_errors = metrics.error_counts
        
        print(f"Actual total_requests: {actual_total}")
        print(f"Actual successful_requests: {actual_successful}")
        print(f"Actual failed_requests: {actual_failed}")
        print(f"Actual avg_response_time: {actual_avg_time}")
        print(f"Actual model_usage: {actual_models}")
        print(f"Actual error_counts: {actual_errors}")
        
        assert actual_total == 0, f"Expected 0, got {actual_total}"
        assert actual_successful == 0, f"Expected 0, got {actual_successful}"
        assert actual_failed == 0, f"Expected 0, got {actual_failed}"
        assert actual_avg_time == 0.0, f"Expected 0.0, got {actual_avg_time}"
        assert actual_models == {}, f"Expected empty dict, got {actual_models}"
        assert actual_errors == {}, f"Expected empty dict, got {actual_errors}"
        
        print("✅ Test passed: OllamaMetrics initial state correct")
    
    def test_record_successful_request(self):
        """Test succesvolle request recording."""
        print("\n🧪 Test: Record successful Ollama request")
        print("Input: llama3:8b model, response_time=1.5s, success=True")
        print("Expected: total=1, successful=1, model_usage['llama3:8b']=1, avg_time=1.5")
        
        metrics = OllamaMetrics()
        response_time = 1.5

        metrics.record_request("llama3:8b", response_time, True)

        actual_total = metrics.total_requests
        actual_successful = metrics.successful_requests
        actual_failed = metrics.failed_requests
        actual_avg_time = metrics.average_response_time
        actual_model_usage = metrics.model_usage.get("llama3:8b", 0)
        
        print(f"Actual total_requests: {actual_total}")
        print(f"Actual successful_requests: {actual_successful}")
        print(f"Actual failed_requests: {actual_failed}")
        print(f"Actual avg_response_time: {actual_avg_time}")
        print(f"Actual model_usage['llama3:8b']: {actual_model_usage}")

        assert actual_total == 1, f"Expected 1, got {actual_total}"
        assert actual_successful == 1, f"Expected 1, got {actual_successful}"
        assert actual_failed == 0, f"Expected 0, got {actual_failed}"
        assert actual_avg_time == 1.5, f"Expected 1.5, got {actual_avg_time}"
        assert actual_model_usage == 1, f"Expected 1, got {actual_model_usage}"
        
        print("✅ Test passed: Successful request recording correct")

    def test_record_failed_request(self):
        """Test mislukte request recording."""
        print("\n🧪 Test: Record failed Ollama request")
        print("Input: llama3:8b model, response_time=2.0s, success=False, error='timeout'")
        print("Expected: total=1, failed=1, error_counts['timeout']=1")
        
        metrics = OllamaMetrics()
        response_time = 2.0

        metrics.record_request("llama3:8b", response_time, False, "timeout")

        actual_total = metrics.total_requests
        actual_successful = metrics.successful_requests
        actual_failed = metrics.failed_requests
        actual_error_count = metrics.error_counts.get("timeout", 0)
        
        print(f"Actual total_requests: {actual_total}")
        print(f"Actual successful_requests: {actual_successful}")
        print(f"Actual failed_requests: {actual_failed}")
        print(f"Actual error_counts['timeout']: {actual_error_count}")

        assert actual_total == 1, f"Expected 1, got {actual_total}"
        assert actual_successful == 0, f"Expected 0, got {actual_successful}"
        assert actual_failed == 1, f"Expected 1, got {actual_failed}"
        assert actual_error_count == 1, f"Expected 1, got {actual_error_count}"
        
        print("✅ Test passed: Failed request recording correct")

    def test_success_rate_calculation(self):
        """Test succes percentage berekening."""
        print("\n🧪 Test: Ollama success rate calculation")
        print("Input: 0 requests, dan 3 succesvol + 1 mislukt")
        print("Expected: 0% voor 0 requests, 75% voor 4 requests")
        
        metrics = OllamaMetrics()

        # Test 0 requests
        expected_rate_0 = 0.0
        actual_rate_0 = metrics.get_success_rate()
        print(f"0 requests - Expected: {expected_rate_0}%, Actual: {actual_rate_0}%")
        assert actual_rate_0 == expected_rate_0, f"Expected {expected_rate_0}%, got {actual_rate_0}%"

        # Test 3 succesvol, 1 mislukt
        metrics.record_request("llama3:8b", 1.0, True)
        metrics.record_request("llama3:8b", 1.5, True)
        metrics.record_request("llama3:8b", 2.0, True)
        metrics.record_request("llama3:8b", 3.0, False, "error")

        expected_rate_4 = 75.0
        actual_rate_4 = metrics.get_success_rate()
        print(f"4 requests (3 succesvol, 1 mislukt) - Expected: {expected_rate_4}%, Actual: {actual_rate_4}%")
        assert actual_rate_4 == expected_rate_4, f"Expected {expected_rate_4}%, got {actual_rate_4}%"
        
        print("✅ Test passed: Success rate calculation correct")


class TestSystemMetrics:
    """Test SystemMetrics class."""
    
    def test_initial_state(self):
        """Test initiële staat van SystemMetrics."""
        metrics = SystemMetrics()
        
        assert isinstance(metrics.start_time, datetime)
        assert metrics.uptime == timedelta(0)
        assert metrics.memory_usage_mb == 0.0
        assert metrics.cpu_usage_percent == 0.0
        assert metrics.active_connections == 0
        assert metrics.total_connections == 0
    
    def test_uptime_update(self):
        """Test uptime update."""
        metrics = SystemMetrics()
        
        # Simuleer tijd verstrijken
        with patch('src.mcp_invoice_processor.monitoring.metrics.datetime') as mock_datetime:
            mock_datetime.now.return_value = metrics.start_time + timedelta(hours=2, minutes=30)
            metrics.update_uptime()
            
            assert metrics.uptime == timedelta(hours=2, minutes=30)
    
    def test_formatted_uptime(self):
        """Test geformatteerde uptime string."""
        metrics = SystemMetrics()
        metrics.uptime = timedelta(hours=5, minutes=42, seconds=18)
        
        formatted = metrics.get_uptime_formatted()
        assert formatted == "05:42:18"


class TestMetricsCollector:
    """Test MetricsCollector class."""
    
    def test_initialization(self):
        """Test initialisatie van MetricsCollector."""
        collector = MetricsCollector()
        
        assert isinstance(collector.processing, ProcessingMetrics)
        assert isinstance(collector.ollama, OllamaMetrics)
        assert isinstance(collector.system, SystemMetrics)
        assert collector._start_times == {}
    
    def test_timer_functionality(self):
        """Test timer functionaliteit."""
        collector = MetricsCollector()
        
        # Start timer
        collector.start_timer("test_operation")
        time.sleep(0.1)  # Wacht even
        
        # Stop timer
        duration = collector.stop_timer("test_operation")
        
        assert duration > 0
        assert "test_operation" not in collector._start_times
    
    def test_document_processing_recording(self):
        """Test document processing metrics recording."""
        collector = MetricsCollector()
        
        collector.record_document_processing("cv", True, 2.5)
        collector.record_document_processing("invoice", False, 1.8, "validation_error")
        
        assert collector.processing.total_documents_processed == 2
        assert collector.processing.successful_documents == 1
        assert collector.processing.failed_documents == 1
        assert collector.processing.cv_documents == 1
        assert collector.processing.invoice_documents == 1
        assert collector.processing.error_counts["validation_error"] == 1
    
    def test_ollama_request_recording(self):
        """Test Ollama request metrics recording."""
        collector = MetricsCollector()
        
        collector.record_ollama_request("llama3:8b", 1.5, True)
        collector.record_ollama_request("llama3:8b", 2.0, False, "timeout")
        
        assert collector.ollama.total_requests == 2
        assert collector.ollama.successful_requests == 1
        assert collector.ollama.failed_requests == 1
        assert collector.ollama.model_usage["llama3:8b"] == 2
        assert collector.ollama.error_counts["timeout"] == 1
    
    def test_comprehensive_metrics(self):
        """Test comprehensive metrics export."""
        collector = MetricsCollector()
        
        # Voeg wat test data toe
        collector.record_document_processing("cv", True, 2.0)
        collector.record_ollama_request("llama3:8b", 1.5, True)
        
        metrics = collector.get_comprehensive_metrics()
        
        assert "timestamp" in metrics
        assert "system" in metrics
        assert "processing" in metrics
        assert "ollama" in metrics
        
        # Controleer specifieke waarden
        assert metrics["processing"]["total_documents"] == 1
        assert metrics["processing"]["successful_documents"] == 1
        assert metrics["ollama"]["total_requests"] == 1
        assert metrics["ollama"]["successful_requests"] == 1
    
    def test_metrics_export_json(self):
        """Test metrics export in JSON formaat."""
        collector = MetricsCollector()
        collector.record_document_processing("cv", True, 2.0)
        
        json_metrics = collector.export_metrics("json")
        
        # Parse JSON om te controleren of het geldig is
        import json
        parsed = json.loads(json_metrics)
        assert "processing" in parsed
        assert parsed["processing"]["total_documents"] == 1
    
    def test_metrics_export_prometheus(self):
        """Test metrics export in Prometheus formaat."""
        collector = MetricsCollector()
        collector.record_document_processing("cv", True, 2.0)
        
        prometheus_metrics = collector.export_metrics("prometheus")
        
        # Controleer of Prometheus format correct is
        assert "# HELP" in prometheus_metrics
        assert "# TYPE" in prometheus_metrics
        assert "mcp_documents_total" in prometheus_metrics
        assert "mcp_documents_successful" in prometheus_metrics
    
    def test_invalid_export_format(self):
        """Test export met ongeldig formaat."""
        collector = MetricsCollector()
        
        with pytest.raises(ValueError, match="Unsupported format"):
            collector.export_metrics("invalid_format")


class TestMetricsIntegration:
    """Test integratie van metrics in de pipeline."""
    
    def test_metrics_collector_singleton(self):
        """Test of metrics_collector een singleton is."""
        from src.mcp_invoice_processor.monitoring.metrics import metrics_collector
        
        # Controleer of het dezelfde instantie is
        collector1 = metrics_collector
        collector2 = metrics_collector
        
        assert collector1 is collector2
    
    def test_metrics_persistence(self):
        """Test of metrics persistent blijven tussen calls."""
        from src.mcp_invoice_processor.monitoring.metrics import metrics_collector
        
        # Reset metrics
        original_total = metrics_collector.processing.total_documents_processed
        
        # Voeg wat data toe
        metrics_collector.record_document_processing("cv", True, 1.0)
        
        # Controleer of het is opgeslagen
        assert metrics_collector.processing.total_documents_processed == original_total + 1


if __name__ == "__main__":
    pytest.main([__file__])
