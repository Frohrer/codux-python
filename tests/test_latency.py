from latency_measure import LatencyMeasurement
import json

def run_latency_tests():
    # Initialize measurement with default settings
    measurement = LatencyMeasurement()
    
    print("Running latency tests...")
    
    # Test cases with different workloads
    test_cases = [
        {
            "name": "Simple console.log",
            "code": "console.log('test')",
            "executions": 10
        },
        {
            "name": "CPU-intensive calculation",
            "code": "console.log(Array(1000000).fill(0).map((x,i) => i*i).reduce((a,b) => a+b, 0))",
            "executions": 5
        },
        {
            "name": "Memory-intensive operation",
            "code": "const arr = Array(10000000).fill(0); console.log(arr.length)",
            "executions": 5
        }
    ]
    
    # Run each test case
    for test in test_cases:
        print(f"\nRunning test: {test['name']}")
        stats = measurement.measure_multiple_executions(
            num_executions=test['executions'],
            code=test['code'],
            delay=0.5  # Half second delay between executions
        )
        
        print(f"Results:")
        print(f"  Mean latency: {stats['mean_ms']:.2f}ms")
        print(f"  Median latency: {stats['median_ms']:.2f}ms")
        print(f"  Min latency: {stats['min_ms']:.2f}ms")
        print(f"  Max latency: {stats['max_ms']:.2f}ms")
        print(f"  Standard deviation: {stats['stdev_ms']:.2f}ms")
        print(f"  Success rate: {stats['success_rate'] * 100:.1f}%")

if __name__ == "__main__":
    run_latency_tests()