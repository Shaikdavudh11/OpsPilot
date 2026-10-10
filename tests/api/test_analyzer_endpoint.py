import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add apps/api to PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from app.main import app

client = TestClient(app)


def test_analyze_endpoint_success():
    payload = {
        "title": "Database connection drop",
        "environment": "production",
        "service_name": "billing-api",
        "raw_logs": "FATAL: connection to server at '10.0.1.25', port 5432 failed: Connection refused. Authorization: Bearer secretToken12345678",
    }

    response = client.post("/api/incidents/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["title"] is not None
    assert data["severity"] in ["low", "medium", "high", "critical"]
    assert "likely_root_cause" in data
    assert "evidence" in data
    assert "recommendations" in data
    assert "prevention" in data
    assert "limitations" in data
    assert data["redacted_secrets_count"] >= 1
    assert data["id"] is not None


def test_analyze_endpoint_validation_error():
    # raw_logs too short
    payload = {
        "title": "Invalid payload",
        "raw_logs": "too short",
    }
    response = client.post("/api/incidents/analyze", json=payload)
    assert response.status_code == 422
