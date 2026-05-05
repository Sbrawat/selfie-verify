# api-demo/api_client.py
import requests

# The URL where your Docker container is listening
API_BASE_URL = "http://localhost:8000/api/v1"

def register_face(username: str, image_bytes: bytes):
    """Sends a multipart/form-data request to the API to register a user."""
    # We package the raw image bytes into a format the API expects
    files = {"file": ("selfie.jpg", image_bytes, "image/jpeg")}
    data = {"username": username}
    
    try:
        response = requests.post(f"{API_BASE_URL}/register", data=data, files=files)
        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        return {"detail": "API is offline. Is Docker running?"}, 500

def verify_face(username: str, image_bytes: bytes):
    """Sends a live image to the API for facial matching."""
    files = {"file": ("selfie.jpg", image_bytes, "image/jpeg")}
    data = {"username": username}
    
    try:
        response = requests.post(f"{API_BASE_URL}/verify", data=data, files=files)
        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        return {"detail": "API is offline. Is Docker running?"}, 500