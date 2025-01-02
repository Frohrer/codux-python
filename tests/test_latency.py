# tests/test_latency_benchmarks.py
import pytest
from latency_measure import LatencyMeasurement

@pytest.fixture
def latency():
    """Fixture for LatencyMeasurement instance"""
    return LatencyMeasurement()

def test_simple_log(latency):
    """Test simple console.log latency"""
    stats = latency.measure_multiple_executions(
        num_executions=5,
        code="console.log('test')",
        delay=0.5
    )
    print(f"\nSimple log stats:")
    print(f"Mean: {stats['mean_ms']:.2f}ms")
    print(f"Median: {stats['median_ms']:.2f}ms")
    print(f"Min: {stats['min_ms']:.2f}ms")
    print(f"Max: {stats['max_ms']:.2f}ms")
    print(f"StdDev: {stats['stdev_ms']:.2f}ms")
    assert stats['success_rate'] > 0

def test_cpu_intensive(latency):
    """Test CPU-intensive calculation latency"""
    stats = latency.measure_multiple_executions(
        num_executions=3,
        code="console.log(Array(1000000).fill(0).map((x,i) => i*i).reduce((a,b) => a+b, 0))",
        delay=0.5
    )
    print(f"\nCPU-intensive stats:")
    print(f"Mean: {stats['mean_ms']:.2f}ms")
    print(f"Median: {stats['median_ms']:.2f}ms")
    print(f"Min: {stats['min_ms']:.2f}ms")
    print(f"Max: {stats['max_ms']:.2f}ms")
    print(f"StdDev: {stats['stdev_ms']:.2f}ms")
    assert stats['success_rate'] > 0

def test_memory_intensive(latency):
    """Test memory-intensive operation latency"""
    stats = latency.measure_multiple_executions(
        num_executions=3,
        code="const arr = Array(10000000).fill(0); console.log(arr.length)",
        delay=0.5
    )
    print(f"\nMemory-intensive stats:")
    print(f"Mean: {stats['mean_ms']:.2f}ms")
    print(f"Median: {stats['median_ms']:.2f}ms")
    print(f"Min: {stats['min_ms']:.2f}ms")
    print(f"Max: {stats['max_ms']:.2f}ms")
    print(f"StdDev: {stats['stdev_ms']:.2f}ms")
    assert stats['success_rate'] > 0