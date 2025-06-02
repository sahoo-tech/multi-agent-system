#!/usr/bin/env python3

import requests
import json

def test_backend():
    url = "http://localhost:8000/intake/"
    
    # Test 1: JSON data
    print("Testing JSON data...")
    data = {"json_body": '{"test": "data", "type": "invoice"}'}
    try:
        response = requests.post(url, data=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Email data
    print("Testing Email data...")
    email_data = {
        "email_body": "From: john@example.com\nSubject: Complaint about service\nI am not satisfied with the service."
    }
    try:
        response = requests.post(url, data=email_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_backend()