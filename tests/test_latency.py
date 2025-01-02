# tests/test_latency.py
import os
import pytest
from unittest.mock import Mock, patch
from latency_measure import LatencyMeasurement

@pytest.fixture
def mock_env_url(monkeypatch):
    """Fixture to set test environment variable"""
    test_url = "http://test-api.example.com/api/v2"
    monkeypatch.setenv("CODUX_API_URL", test_url)
    return test_url

@pytest.fixture
def mock_client():
    """Fixture to create a mock CodeExecutionClient"""
    with patch('latency_measure.CodeExecutionClient') as mock:
        client = Mock()
        mock.return_value = client
        yield client

def test_initialization_with_env_url(mock_env_url):
    """Test that LatencyMeasurement uses environment URL"""
    measurement = LatencyMeasurement()
    assert measurement.base_url == mock_env_url

def test_initialization_with_override_url(mock_env_url):
    """Test that provided URL overrides environment URL"""
    override_url = "http://override-api.example.com/api/v2"
    measurement = LatencyMeasurement(base_url=override_url)
    assert measurement.base_url == override_url

def test_measure_single_execution_success(mock_client):
    """Test successful single execution measurement"""
    mock_client.execute_code.return_value = {"output": "test"}
    measurement = LatencyMeasurement()
    
    latency = measurement.measure_single_execution()
    
    assert isinstance(latency, float)
    assert latency > 0
    assert len(measurement.results) == 1
    assert measurement.results[0]["success"] is True

def test_measure_single_execution_failure(mock_client):
    """Test failed single execution measurement"""
    mock_client.execute_code.side_effect = Exception("Test error")
    measurement = LatencyMeasurement()
    
    latency = measurement.measure_single_execution()
    
    assert isinstance(latency, float)
    assert latency > 0
    assert len(measurement.results) == 1
    assert measurement.results[0]["success"] is False
    assert "Test error" in measurement.results[0]["error"]

def test_measure_multiple_executions(mock_client):
    """Test multiple executions measurement"""
    mock_client.execute_code.return_value = {"output": "test"}
    measurement = LatencyMeasurement()
    
    num_executions = 5
    stats = measurement.measure_multiple_executions(
        num_executions=num_executions,
        delay=0  # No delay for testing
    )
    
    assert len(measurement.results) == num_executions
    assert stats["num_samples"] == num_executions
    assert stats["success_rate"] == 1.0
    assert all(key in stats for key in [
        "min_ms", "max_ms", "mean_ms", "median_ms", "stdev_ms"
    ])