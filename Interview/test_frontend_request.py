#!/usr/bin/env python3

import requests
import json

def test_frontend_like_request():
    """Test the backend with a request that mimics what the frontend sends"""
    url = "http://localhost:8000/intake/"
    
    # Create form data like the frontend does
    files = {'json_body': (None, '{"test": "data", "type": "invoice"}')}
    
    headers = {
        'Origin': 'http://localhost:3000',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print("Sending request...")
        response = requests.post(url, files=files, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Parsed JSON: {json.dumps(data, indent=2)}")
        
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_frontend_like_request()