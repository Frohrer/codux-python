import requests
import websockets
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union

class PackageAlreadyInstalledError(Exception):
    """Raised when attempting to install an already installed package"""
    pass

class PackageNotFoundError(Exception):
    """Raised when a package is not found"""
    pass

class CodeExecutionError(Exception):
    """Generic error for code execution issues"""
    pass

@dataclass
class Runtime:
    language: str
    version: str
    runtime: Optional[str] = None
    aliases: List[str] = field(default_factory=list)

@dataclass
class Package:
    language: str
    language_version: str
    installed: bool

@dataclass
class ExecutionResult:
    install_output: Optional[str] = None
    install_error: Optional[str] = None
    execute_output: Optional[str] = None
    execute_error: Optional[str] = None
    web_app_url: Optional[str] = None

class CodeExecutionClient:
    def __init__(
        self, 
        base_url: str = "http://localhost/api/v2", 
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the CodeExecutionClient
        
        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            headers: Optional dictionary of default headers to include in all requests
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            headers: Optional additional headers for this specific request
            **kwargs: Additional arguments passed to requests.request()
            
        Returns:
            Dict containing the JSON response
            
        Raises:
            PackageNotFoundError: When a package is not found
            PackageAlreadyInstalledError: When attempting to install an existing package
            CodeExecutionError: For other API errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Merge request-specific headers with session headers
        if headers:
            request_headers = self.session.headers.copy()
            request_headers.update(headers)
            kwargs['headers'] = request_headers
            
        try:
            response = self.session.request(method=method, url=url, timeout=self.timeout, **kwargs)
            
            if response.status_code == 404:
                raise PackageNotFoundError(response.json().get('message', 'Package not found'))
            elif response.status_code == 409 and endpoint == 'packages':
                raise PackageAlreadyInstalledError(response.json().get('message', 'Package already installed'))
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError):
                try:
                    error_msg = e.response.json().get('message', str(e))
                except json.JSONDecodeError:
                    error_msg = str(e)
                raise CodeExecutionError(f"API request failed: {error_msg}")
            raise CodeExecutionError(f"API request failed: {str(e)}")

    def list_runtimes(self, headers: Optional[Dict[str, str]] = None) -> List[Runtime]:
        """
        List available runtimes
        
        Args:
            headers: Optional headers for this request
            
        Returns:
            List of Runtime objects
        """
        response = self._make_request("GET", "/runtimes", headers=headers)
        return [Runtime(**runtime) for runtime in response]

    def list_packages(self, headers: Optional[Dict[str, str]] = None) -> List[Package]:
        """
        List installed packages
        
        Args:
            headers: Optional headers for this request
            
        Returns:
            List of Package objects
        """
        response = self._make_request("GET", "/packages", headers=headers)
        return [Package(**package) for package in response]

    def install_package(
        self, 
        language: str, 
        version: str, 
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Install a package
        
        Args:
            language: Programming language
            version: Language version
            headers: Optional headers for this request
            
        Returns:
            True if package was installed, False if already installed
        """
        payload = {"language": language, "version": version}
        try:
            self._make_request("POST", "/packages", json=payload, headers=headers)
            return True
        except PackageAlreadyInstalledError:
            return False

    def uninstall_package(
        self, 
        language: str, 
        version: str, 
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Uninstall a package
        
        Args:
            language: Programming language
            version: Language version
            headers: Optional headers for this request
        """
        payload = {"language": language, "version": version}
        self._make_request("DELETE", "/packages", json=payload, headers=headers)

    def terminate_process(
        self, 
        process_id: str, 
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Terminate a running process
        
        Args:
            process_id: ID of the process to terminate
            headers: Optional headers for this request
        """
        self._make_request("DELETE", f"/process/{process_id}", headers=headers)

    async def connect_websocket(
        self,
        headers: Optional[Dict[str, str]] = None
    ) -> websockets.WebSocketClientProtocol:
        """
        Connect to the WebSocket endpoint
        
        Args:
            headers: Optional headers for the WebSocket connection
            
        Returns:
            WebSocket connection object
        """
        ws_url = f"ws://{self.base_url.split('://', 1)[1]}/connect"
        return await websockets.connect(ws_url, extra_headers=headers)

    def execute_code(
        self,
        code: str,
        language: str,
        version: str,
        name: str = "main",
        encoding: str = "utf8",
        dependencies: Optional[List[str]] = None,
        args: Optional[List[str]] = None,
        stdin: Optional[str] = None,
        compile_memory_limit: Optional[float] = None,
        run_memory_limit: Optional[float] = None,
        run_timeout: Optional[float] = None,
        compile_timeout: Optional[float] = None,
        run_cpu_time: Optional[float] = None,
        compile_cpu_time: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        Execute code in the specified programming language
        
        Args:
            code: The source code to execute
            language: Programming language
            version: Language version
            name: Name of the file (defaults to "main")
            encoding: File encoding (defaults to "utf8")
            dependencies: Optional list of dependencies
            args: Optional command line arguments
            stdin: Optional standard input
            compile_memory_limit: Optional compile memory limit
            run_memory_limit: Optional run memory limit
            run_timeout: Optional run timeout
            compile_timeout: Optional compile timeout
            run_cpu_time: Optional run CPU time limit
            compile_cpu_time: Optional compile CPU time limit
            headers: Optional headers for this request
        
        Returns:
            ExecutionResult object containing execution results
        """
        payload = {
            "language": language,
            "version": version,
            "files": [{
                "name": name,
                "content": code,
                "encoding": encoding
            }]
        }

        if dependencies is not None:
            payload["dependencies"] = dependencies
        if args is not None:
            payload["args"] = args
        if stdin is not None:
            payload["stdin"] = stdin
        if compile_memory_limit is not None:
            payload["compile_memory_limit"] = compile_memory_limit
        if run_memory_limit is not None:
            payload["run_memory_limit"] = run_memory_limit
        if run_timeout is not None:
            payload["run_timeout"] = run_timeout
        if compile_timeout is not None:
            payload["compile_timeout"] = compile_timeout
        if run_cpu_time is not None:
            payload["run_cpu_time"] = run_cpu_time
        if compile_cpu_time is not None:
            payload["compile_cpu_time"] = compile_cpu_time

        response = self._make_request("POST", "/execute", json=payload, headers=headers)
        
        result = ExecutionResult()
        
        if "stages" in response:
            stages = response["stages"]
            if "install" in stages:
                result.install_output = stages["install"].get("stdout")
                result.install_error = stages["install"].get("stderr")
            if "execute" in stages:
                result.execute_output = stages["execute"].get("stdout")
                result.execute_error = stages["execute"].get("stderr")
        
        if "webAppUrl" in response:
            result.web_app_url = response["webAppUrl"]
            
        return result