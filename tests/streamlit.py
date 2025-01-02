from codux.src.codux.main import CodeExecutionClient

client = CodeExecutionClient(base_url="http://code-api.home/api/v2")
    
result = client.execute_code(
    language="streamlit",
    version="3.11.0",
    code="""import streamlit as st
import pandas as pd
import numpy as np

# Set page title
st.title('Simple Streamlit Demo')
""",
)

print(result.web_app_url)
