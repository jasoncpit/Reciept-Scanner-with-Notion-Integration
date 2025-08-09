'''
Author: @jason-template
Date: 2025-07-27
pytest scripts for the API 
'''

import pytest
import os
from fastapi.testclient import TestClient
from io import BytesIO
from unittest.mock import patch
from importlib import reload
import app.main

# We'll create the client fresh for each test that needs auth testing
client = TestClient(app.main.app)

def test_health():
    """Test the health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_scan_without_auth():
    """Test scan endpoint without authentication when no AUTH_TOKEN is set"""
    # Create a dummy file
    file_content = b"fake image content"
    files = {"file": ("test_receipt.jpg", BytesIO(file_content), "image/jpeg")}
    
    response = client.post("/scan", files=files)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    
@patch.dict(os.environ, {"AUTH_TOKEN": "test_token"})
def test_scan_with_invalid_auth():
    """Test scan endpoint with invalid authentication when AUTH_TOKEN is set"""
    # Create a dummy file
    file_content = b"fake image content"
    files = {"file": ("test_receipt.jpg", BytesIO(file_content), "image/jpeg")}
    
    # Reload the module to pick up the new environment variable
    reload(app.main)
    test_client = TestClient(app.main.app)
    
    # Test with invalid auth
    response = test_client.post("/scan", files=files, headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

def test_scan_with_valid_auth():
    """Test scan endpoint with valid authentication when AUTH_TOKEN is set"""
    # Create a dummy file
    file_content = b"fake image content"
    files = {"file": ("test_receipt.jpg", BytesIO(file_content), "image/jpeg")}
    
    # Reload the module to pick up the new environment variable
    reload(app.main)
    test_client = TestClient(app.main.app, base_url="http://localhost:8000", headers={"Authorization": "Bearer GabAva!7"})
    
    # Test with valid auth
    response = test_client.post("/scan", files=files, headers={"Authorization": "Bearer GabAva!7"})
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_scan_missing_file():
    """Test scan endpoint without providing a file"""
    response = client.post("/scan")
    assert response.status_code == 422  # Unprocessable Entity for missing required field

if __name__ == "__main__":
    pytest.main()
