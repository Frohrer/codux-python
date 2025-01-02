# src/latency_measure/main.py
import os
import time
import statistics
import json
from typing import List, Dict
from codux.src.codux.main import CodeExecutionClient, ExecutionResult

class LatencyMeasurement:
    def __init__(self, base_url: str = None):
        """
        Initialize the LatencyMeasurement class
        Args:
            base_url: Optional URL override. If not provided, uses CODUX_API_URL environment variable
        """
        self.base_url = base_url or os.getenv('CODUX_API_URL', 'http://localhost/api/v2')
        self.client = CodeExecutionClient(base_url=self.base_url)
        self.results: List[Dict] = []

    def measure_single_execution(
        self, 
        code: str = "console.log(Array(1000000).fill(0).map((x,i) => i*i).reduce((a,b) => a+b, 0))",
        language: str = "javascript",
        version: str = "20.11.1"
    ) -> float:
        """
        Measure the latency of a single code execution
        Returns the latency in milliseconds
        """
        start_time = time.perf_counter()
        
        try:
            result = self.client.execute_code(
                language=language,
                version=version,
                code=code
            )
            end_time = time.perf_counter()
            latency = (end_time - start_time) * 1000  # Convert to milliseconds
            
            execution_data = {
                "timestamp": time.time(),
                "latency_ms": latency,
                "success": True,
                "result": result
            }
            
        except Exception as e:
            end_time = time.perf_counter()
            latency = (end_time - start_time) * 1000
            
            execution_data = {
                "timestamp": time.time(),
                "latency_ms": latency,
                "success": False,
                "error": str(e)
            }
            
        self.results.append(execution_data)
        return latency

    def measure_multiple_executions(
        self,
        num_executions: int = 10,
        code: str = "console.log('test')",
        language: str = "javascript",
        version: str = "20.11.1",
        delay: float = 0.1
    ) -> Dict:
        """
        Measure latency over multiple executions and return statistics
        Args:
            num_executions: Number of executions to perform
            code: Code to execute
            language: Programming language
            version: Language version
            delay: Delay between executions in seconds
        """
        latencies = []
        
        for _ in range(num_executions):
            latency = self.measure_single_execution(code, language, version)
            latencies.append(latency)
            if delay > 0:
                time.sleep(delay)
            
        stats = {
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "stdev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "num_samples": len(latencies),
            "success_rate": sum(r["success"] for r in self.results[-num_executions:]) / num_executions
        }
        
        return stats

    def get_detailed_results(self) -> str:
        """
        Return detailed results in a formatted string
        """
        return json.dumps(self.results, indent=2)

def main():
    # Get URL from environment variable
    api_url = os.getenv('CODUX_API_URL')
    if not api_url:
        print("Warning: CODUX_API_URL not set, using default")
    
    # Initialize measurement
    latency_measure = LatencyMeasurement(api_url)
    
    # Measure single execution
    print("Single execution latency:", latency_measure.measure_single_execution(), "ms")
    
    # Measure multiple executions
    stats = latency_measure.measure_multiple_executions(num_executions=100)
    print("\nLatency statistics over 100 executions:")
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()