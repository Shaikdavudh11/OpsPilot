import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add apps/api to PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from app.main import app

client = TestClient(app)


def test_health_check_returns_healthy():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "OpsPilot API"
    assert "version" in data
    assert "ai_provider" in data
    assert "timestamp" in data
