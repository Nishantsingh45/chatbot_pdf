import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_pdf():
    with open("test.pdf", "rb") as f:
        response = client.post("/upload-pdf", files={"file": ("test.pdf", f, "application/pdf")})
    assert response.status_code == 200
    assert response.json() == {"message": "PDF uploaded, saved, and processed successfully"}

def test_upload_non_pdf():
    with open("test.txt", "rb") as f:
        response = client.post("/upload-pdf", files={"file": ("test.txt", f, "text/plain")})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file format. Please upload a PDF file."}

def test_chat_without_pdf():
    response = client.post("/chat", data={"query": "Hello"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Please upload a PDF file first."}

def test_chat_with_pdf():
    # First, upload a PDF
    with open("test.pdf", "rb") as f:
        client.post("/upload-pdf", files={"file": ("test.pdf", f, "application/pdf")})
    
    # Now, test the chat endpoint
    response = client.post("/chat", data={"query": "What is this document about?"})
    assert response.status_code == 200
    assert "response" in response.json()