import unittest
from codux.src.codux.main import CodeExecutionClient, ExecutionResult, CodeExecutionError

class TestCodeExecution(unittest.TestCase):
    def setUp(self):
        self.client = CodeExecutionClient(base_url="http://code-api.home/api/v2")
        
    def test_hello_world(self):
        result = self.client.execute_code(
            language="python",
            version="3.11.0",
            code='print("Hello, World!")',
        )
        
        self.assertIsInstance(result, ExecutionResult)
        self.assertEqual(result.execute_output.strip(), "Hello, World!")
        # self.assertEqual(result.execute_error, 0)

    def test_list_runtimes(self):
        runtimes = self.client.list_runtimes()
        self.assertTrue(isinstance(runtimes, list))
        if runtimes:
            self.assertTrue(all(hasattr(r, 'language') and hasattr(r, 'version') for r in runtimes))

    def test_package_management(self):
        # Get initial packages
        initial_packages = self.client.list_packages()
        
        # Try to install Python runtime - should return False if already installed
        # was_installed = self.client.install_package("python", "3.11.0")
        
        # Get updated package list
        updated_packages = self.client.list_packages()
        print(updated_packages)
        # Python should be in the list and installed
        python_package = next(
            (p for p in updated_packages 
             if p.language == "python" and p.language_version == "3.11.0"),
            None
        )
        self.assertIsNotNone(python_package)
        self.assertTrue(python_package.installed)

def run_hello_world():
    client = CodeExecutionClient(base_url="http://code-api.home/api/v2")
    
    result = client.execute_code(
        language="python",
        version="3.11.0",
        code='print("Hello, World!")',
    )
    
    print("\nExecution Results:")
    print("-----------------")
    if result.execute_output:
        print("Output:", result.execute_output.strip())
    if result.execute_error:
        print("Error:", result.execute_error)
    if result.execute_error is not None:
        print("Exit code:", result.execute_error)
    if result.web_app_url:
        print("Web App URL:", result.web_app_url)

if __name__ == "__main__":
    print("Running Hello World example...")
    run_hello_world()
    print("\nRunning unit tests...")
    unittest.main(argv=[''], exit=False)