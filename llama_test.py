# Create a new file: test_llm.py

import requests
import json
import sys

def test_llama_api():
    """Test if the Llama API is working correctly"""
    api_url = "http://localhost:11434/api/generate"  # Change if needed
    
    # Test with your example payload
    payload = {
        "model": "llama3.2:3b",
        "prompt": "python is highlevel yes! or no!? with exclamation after yes and no",
        "stream": False
    }
    
    try:
        print("Testing Llama API...")
        print(f"API URL: {api_url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(api_url, json=payload, timeout=30)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("API Test Successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_llama_api()
    sys.exit(0 if success else 1)