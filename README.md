# codux

A Python library for executing code remotely and measuring execution latency. This library provides both a general-purpose code execution client and a specialized latency measurement tool.

## Features

- Execute code in multiple programming languages
- Manage runtime environments and packages
- WebSocket support for real-time communication
- Custom headers support for authentication and configuration
- Comprehensive latency measurement tools
- Detailed execution statistics and reporting

## Installation

```bash
pip install codux
```

## Basic Usage

### Code Execution Client

```python
from codux import CodeExecutionClient

# Initialize the client
client = CodeExecutionClient(
    base_url="http://your-api-url/api/v2",
    timeout=30,
    headers={"Authorization": "Bearer your-token"}
)

# Execute code
result = client.execute_code(
    code="print('Hello, World!')",
    language="python",
    version="3.9"
)

print(result.execute_output)
```

### Latency Measurement

```python
from latency_measure import LatencyMeasurement

# Initialize the measurement tool
latency = LatencyMeasurement()

# Run a single test
single_latency = latency.measure_single_execution(
    code="console.log('test')",
    language="javascript",
    version="20.11.1"
)

# Run multiple tests and get statistics
stats = latency.measure_multiple_executions(
    num_executions=100,
    delay=0.1
)

print(f"Median latency: {stats['median_ms']}ms")
```

## Environment Variables

The library uses the following environment variables:

### Required

- `CODUX_API_URL`: Base URL for the API (default: http://localhost/api/v2)

### Optional Headers

- `CODUX_HEADER1_NAME`: Name of the first custom header
- `CODUX_HEADER1_VALUE`: Value of the first custom header
- `CODUX_HEADER2_NAME`: Name of the second custom header
- `CODUX_HEADER2_VALUE`: Value of the second custom header

Example configuration:

```bash
export CODUX_API_URL="http://api.example.com/api/v2"
export CODUX_HEADER1_NAME="Authorization"
export CODUX_HEADER1_VALUE="Bearer token123"
export CODUX_HEADER2_NAME="X-Custom-Header"
export CODUX_HEADER2_VALUE="custom-value"
```

## Advanced Features

### Custom Headers

You can set headers both globally and per-request:

```python
# Global headers during initialization
client = CodeExecutionClient(
    headers={
        "Authorization": "Bearer token123",
        "X-Custom-Header": "value"
    }
)

# Per-request headers
result = client.execute_code(
    code="print('Hello')",
    language="python",
    version="3.9",
    headers={"X-Request-ID": "123"}
)
```

### Package Management

```python
# List available runtimes
runtimes = client.list_runtimes()

# List installed packages
packages = client.list_packages()

# Install a package
client.install_package(language="python", version="3.9")

# Uninstall a package
client.uninstall_package(language="python", version="3.9")
```

### WebSocket Connection

```python
async def connect_websocket():
    ws = await client.connect_websocket()
    # Use the WebSocket connection
    await ws.send("Hello")
    response = await ws.recv()
    print(response)
```

### Execution Options

The `execute_code` method supports various execution options:

```python
result = client.execute_code(
    code="print('Hello')",
    language="python",
    version="3.9",
    name="main.py",
    encoding="utf8",
    dependencies=["requests==2.26.0"],
    args=["--verbose"],
    stdin="input data",
    compile_memory_limit=512,
    run_memory_limit=1024,
    run_timeout=30,
    compile_timeout=10,
    run_cpu_time=20,
    compile_cpu_time=5
)
```

### Latency Measurement Statistics

The latency measurement tool provides detailed statistics:

```python
stats = latency.measure_multiple_executions(num_executions=100)

print(f"""
Statistics:
- Minimum latency: {stats['min_ms']}ms
- Maximum latency: {stats['max_ms']}ms
- Mean latency: {stats['mean_ms']}ms
- Median latency: {stats['median_ms']}ms
- Standard deviation: {stats['stdev_ms']}ms
- Success rate: {stats['success_rate'] * 100}%
""")

# Get detailed results in JSON format
detailed_results = latency.get_detailed_results()
```

## Error Handling

The library provides custom exceptions for common error cases:

```python
from codux import (
    PackageAlreadyInstalledError,
    PackageNotFoundError,
    CodeExecutionError
)

try:
    client.install_package(language="python", version="3.9")
except PackageAlreadyInstalledError:
    print("Package is already installed")
except PackageNotFoundError:
    print("Package not found")
except CodeExecutionError as e:
    print(f"Execution failed: {e}")
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
