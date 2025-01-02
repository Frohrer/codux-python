import unittest
from codux.src.codux.main import CodeExecutionClient

class IsolateSecurityTestSuite(unittest.TestCase):
    def setUp(self):
        """Setup method to initialize the CodeExecutionClient."""
        self.client = CodeExecutionClient(base_url="http://code-api.home/api/v2")
        self.base_assertion_msg = "Security violation - "

    def test_fifo_ipc(self):
        """Test if named pipes (FIFOs) are blocked."""
        code = """
import os
import sys

def attempt_fifo_creation():
    fifo_path = "/tmp/test_fifo"
    try:
        os.mkfifo(fifo_path)
        # If we get here, cleanup to be thorough
        os.unlink(fifo_path)
        return "FIFO creation succeeded"
    except OSError as e:
        return f"Error: {e}"

print(attempt_fifo_creation())
"""
        result = self.client.execute_code(language="python", version="3.11.0", code=code)
        self.assertNotIn("FIFO creation succeeded", result.execute_output,
                        self.base_assertion_msg + "FIFO creation was not blocked")
        if "FIFO creation succeeded" in result.execute_output:
            self.fail(self.base_assertion_msg + "FIFO was successfully created when it should be blocked")

    def test_unix_socket_ipc(self):
        """Test if Unix domain sockets are blocked."""
        code = """
import socket
import os

def attempt_socket_creation():
    socket_path = "/tmp/test_socket"
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.bind(socket_path)
            # If we get here, cleanup
            os.unlink(socket_path)
            return "Socket creation succeeded"
    except OSError as e:
        return f"Error: {e}"

print(attempt_socket_creation())
"""
        result = self.client.execute_code(language="python", version="3.11.0", code=code)
        self.assertNotIn("Socket creation succeeded", result.execute_output,
                        self.base_assertion_msg + "Unix socket creation was not blocked")
        if "Socket creation succeeded" in result.execute_output:
            self.fail(self.base_assertion_msg + "Unix socket was successfully created when it should be blocked")

    def test_shared_memory_ipc(self):
        """Test if shared memory is blocked."""
        code = """
import mmap
import contextlib

def attempt_shared_memory():
    try:
        with contextlib.closing(mmap.mmap(-1, 1024, tagname="test_shm")) as mm:
            mm.write(b"test")
            return "Shared memory creation succeeded"
    except Exception as e:
        return f"Error: {e}"

print(attempt_shared_memory())
"""
        result = self.client.execute_code(language="python", version="3.11.0", code=code)
        self.assertNotIn("Shared memory creation succeeded", result.execute_output,
                        self.base_assertion_msg + "Shared memory creation was not blocked")
        if "Shared memory creation succeeded" in result.execute_output:
            self.fail(self.base_assertion_msg + "Shared memory was successfully created when it should be blocked")

    def test_file_write_persistence(self):
        """Test if writing to files outside the sandbox is blocked."""
        code = """
import os
import tempfile

def attempt_file_write():
    try:
        # Attempt to write to various sensitive locations
        paths = [
            "/etc/test_file",
            "/tmp/test_file",
            "~/test_file",
            "/var/log/test_file",
            "./test_file"  # Even current directory should be restricted
        ]
        
        results = []
        for path in paths:
            try:
                with open(os.path.expanduser(path), "w") as f:
                    f.write("test content")
                results.append(f"Success: Wrote to {path}")
            except OSError as e:
                results.append(f"Error: {e} (path: {path})")
        
        return "\\n".join(results)
    except Exception as e:
        return f"Unexpected error: {e}"

print(attempt_file_write())
"""
        result = self.client.execute_code(language="python", version="3.11.0", code=code)
        self.assertNotIn("Success:", result.execute_output,
                        self.base_assertion_msg + "File writing was not blocked")
        if "Success:" in result.execute_output:
            self.fail(self.base_assertion_msg + "Successfully wrote to a file when it should be blocked")

    def test_file_read_restrictions(self):
        """Test if reading sensitive files is blocked."""
        code = """
import os

def attempt_file_reads():
    sensitive_files = [
        "/etc/passwd",
        "/etc/shadow",
        "/proc/self/environ",
        "/proc/self/maps",
        "~/.ssh/id_rsa"
    ]
    
    results = []
    for filepath in sensitive_files:
        try:
            with open(os.path.expanduser(filepath), "r") as f:
                content = f.read()
                results.append(f"Success: Read {filepath}")
        except OSError as e:
            results.append(f"Error: {e} (file: {filepath})")
    
    return "\\n".join(results)

print(attempt_file_reads())
"""
        result = self.client.execute_code(language="python", version="3.11.0", code=code)
        self.assertNotIn("Success:", result.execute_output,
                        self.base_assertion_msg + "Sensitive file reading was not blocked")
        if "Success:" in result.execute_output:
            self.fail(self.base_assertion_msg + "Successfully read a sensitive file when it should be blocked")

    def test_network_access(self):
        """Test if network access is blocked."""
        code = """
import socket
import urllib.request
import subprocess

def attempt_network_access():
    results = []
    
    # Test raw socket
    try:
        socket.create_connection(("8.8.8.8", 53))
        results.append("Success: Raw socket connection worked")
    except OSError as e:
        results.append(f"Error: Raw socket - {e}")
    
    # Test high-level HTTP
    try:
        urllib.request.urlopen("http://example.com")
        results.append("Success: HTTP request worked")
    except Exception as e:
        results.append(f"Error: HTTP request - {e}")
    
    # Test localhost
    try:
        socket.create_connection(("127.0.0.1", 80))
        results.append("Success: Localhost connection worked")
    except OSError as e:
        results.append(f"Error: Localhost - {e}")
    
    return "\\n".join(results)

print(attempt_network_access())
"""
        result = self.client.execute_code(language="python", version="3.11.0", code=code)
        self.assertNotIn("Success:", result.execute_output,
                        self.base_assertion_msg + "Network access was not blocked")
        if "Success:" in result.execute_output:
            self.fail(self.base_assertion_msg + "Network access succeeded when it should be blocked")

    def test_process_creation(self):
        """Test if process creation and execution is blocked."""
        code = """
import os
import subprocess
import multiprocessing

def attempt_process_creation():
    results = []
    
    # Test fork
    try:
        pid = os.fork()
        results.append("Success: Fork worked")
    except OSError as e:
        results.append(f"Error: Fork - {e}")
    
    # Test subprocess
    try:
        subprocess.run(["ls"], capture_output=True)
        results.append("Success: Subprocess worked")
    except Exception as e:
        results.append(f"Error: Subprocess - {e}")
    
    # Test multiprocessing
    try:
        p = multiprocessing.Process(target=lambda: None)
        p.start()
        results.append("Success: Multiprocessing worked")
    except Exception as e:
        results.append(f"Error: Multiprocessing - {e}")
    
    return "\\n".join(results)

print(attempt_process_creation())
"""
        result = self.client.execute_code(language="python", version="3.11.0", code=code)
        self.assertNotIn("Success:", result.execute_output,
                        self.base_assertion_msg + "Process creation was not blocked")
        if "Success:" in result.execute_output:
            self.fail(self.base_assertion_msg + "Process creation succeeded when it should be blocked")

    def test_system_resources(self):
        """Test if access to system resources and information is blocked."""
        code = """
import os
import psutil
import resource

def attempt_system_access():
    results = []
    
    # Try to get system information
    try:
        psutil.cpu_percent()
        results.append("Success: Got CPU info")
    except Exception as e:
        results.append(f"Error: CPU info - {e}")
    
    # Try to modify process limits
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (1024, 1024))
        results.append("Success: Modified resource limits")
    except Exception as e:
        results.append(f"Error: Resource limits - {e}")
    
    # Try to get process environment
    try:
        os.environ["PATH"]
        results.append("Success: Accessed environment variables")
    except Exception as e:
        results.append(f"Error: Environment access - {e}")
    
    return "\\n".join(results)

print(attempt_system_access())
"""
        result = self.client.execute_code(language="python", version="3.11.0", code=code)
        # Note: Some of these might be allowed depending on your security policy
        self.assertNotIn("Success:", result.execute_output,
                        self.base_assertion_msg + "System resource access was not properly restricted")
        if "Success:" in result.execute_output:
            self.fail(self.base_assertion_msg + "System resource access succeeded when it should be blocked")
            
    def test_disk_space_exhaustion(self):
        """Test if large file creation for disk space exhaustion is blocked."""
        code = """
with open("beans","w") as f:
    n = 2**24
    f.write("I love beans\\n"*n)
"""
        result = self.client.execute_code(language="python", version="3.11.0", code=code)
        self.assertIn("Error", result.execute_output,
                     self.base_assertion_msg + "Large file creation was not blocked")
        
    def test_world_writable_directories(self):
        """Test if writing to world-writable directories is properly cleaned up."""
        code = """
import os
directories = [
    "/dev/shm",
    "/run/lock",
    "/tmp",
    "/var/tmp"
]
for dir in directories:
    fpath = f"{dir}/bean"
    if os.path.exists(fpath):
        print(f"{fpath} exists")
    else:
        with open(fpath, "w") as f:
            f.write("beannn")
"""
        # Run test twice to verify cleanup
        for _ in range(2):
            result = self.client.execute_code(language="python", version="3.11.0", code=code)
            self.assertEqual("", result.execute_output.strip(),
                           self.base_assertion_msg + "Files persisted in world-writable directories")

    def test_fork_bomb_prevention(self):
        """Test if fork bomb attempts are prevented."""
        code = """
import os
while True:
    try:
        os.fork()
    except:
        pass
"""
        result = self.client.execute_code(language="python", version="3.11.0", code=code)
        self.assertIn("Error", result.execute_output,
                     self.base_assertion_msg + "Fork bomb attempt was not blocked")

    def test_runaway_output(self):
        """Test if infinite output generation is properly contained."""
        code = """
while True:
    print("Piston is secure")
"""
        result = self.client.execute_code(language="python", version="3.11.0", code=code)
        self.assertIn("Error", result.execute_output,
                     self.base_assertion_msg + "Infinite output was not contained")
        self.assertTrue(len(result.execute_output) < 1000000,  # Adjust size limit as needed
                       self.base_assertion_msg + "Output size was not properly limited")

if __name__ == '__main__':
    unittest.main()