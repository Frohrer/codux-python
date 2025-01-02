from codux.src.codux.main import CodeExecutionClient

client = CodeExecutionClient(base_url="http://code-api.home/api/v2")
    
result = client.execute_code(
    language="python",
    version="3.12.8",
    code="""
import requests

def get_page_content():
    try:
        # Make a GET request to the page
        response = requests.get('http://192.168.1.2/', timeout=5)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Print the page content
        print(response.text)
        
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_page_content()
""",
)

print(result)
