import requests

api_url = "http://127.0.0.1:8000/predict"

website_url = "https://example.com"

payload = {"url": website_url}

response = requests.post(api_url, json=payload)

if response.status_code == 200:
    print("Prediction successful!")
    print("Response:", response.json())
else:
    print("Failed to get prediction")
    print("Status code:", response.status_code)
    print("Response:", response.text)
