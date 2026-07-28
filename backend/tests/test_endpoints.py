import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_test_endpoint():
    """Test POST /test endpoint"""
    response = client.post("/test", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_list_documents_empty():
    """Test listing documents"""
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)