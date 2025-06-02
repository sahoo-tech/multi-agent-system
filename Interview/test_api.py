import requests

def test_json_input():
    url = "http://127.0.0.1:8000/intake/"
    json_body = '{"id": "123", "type": "order", "attributes": {"item": "book"}}'
    files = {
        'json_body': (None, json_body),
    }
    response = requests.post(url, files=files)
    print("JSON Input Test Response:", response.json())

def test_email_input():
    url = "http://127.0.0.1:8000/intake/"
    email_body = """From: John Doe <john@example.com>
Subject: RFQ for office supplies
Urgency: ASAP
Conversation-ID: 789

Please send a quote for 100 pens."""
    files = {
        'email_body': (None, email_body),
    }
    response = requests.post(url, files=files)
    print("Email Input Test Response:", response.json())

def test_no_input():
    url = "http://127.0.0.1:8000/intake/"
    response = requests.post(url)
    print("No Input Test Response:", response.json())

if __name__ == "__main__":
    test_json_input()
    test_email_input()
    test_no_input()
