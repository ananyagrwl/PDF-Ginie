import pytest
import requests
from fastapi.testclient import TestClient
from app import app

base_url = "http://localhost:8000"


# Fixture to provide a TestClient for HTTP tests
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health():
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_upload_pdf_invalid_type():
    text_content = b"This is a text file"
    files = {"file": ("example.txt", text_content, "text/plain")}
    response = requests.post(f"{base_url}/upload/", files=files)
    assert response.status_code == 400
    assert response.json() == {"detail": "File must be a PDF"}

def test_get_all_pdfs():
    response = requests.get(f"{base_url}/get_all_pdfs/")
    assert response.status_code == 200
    assert "pdfs" in response.json()

def test_websocket_qa():
    import websocket
    uri = "ws://127.0.0.1:8000/ws/qa/"
    ws = websocket.create_connection(uri)
    ws.send('{"pdf_id": "invalid_id", "question": "What is this?"}')
    response = ws.recv()
    ws.close()
    import json
    response_data = json.loads(response)
    assert response_data.get("error") == "Document not found."