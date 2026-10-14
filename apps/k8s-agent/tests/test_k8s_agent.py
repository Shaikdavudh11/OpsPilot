from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8002


def test_get_sample_repos():
    response = client.get("/api/k8s/sample-repos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_troubleshoot_oomkilled():
    payload = {
        "pod_name": "checkout-service-849204-xz91a",
        "namespace": "ecommerce",
        "failure_type": "OOMKilled",
        "describe_output": "State: Terminated\nReason: OOMKilled\nExit Code: 137\nLast State: Terminated",
        "pod_logs": "FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory",
    }
    response = client.post("/api/k8s/troubleshoot-pod", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["detected_issue"] == "OOMKilled (Out of Memory - Exit Code 137)"
    assert data["confidence"] == "high"
    assert "1536Mi" in data["yaml_patch"]


def test_troubleshoot_crashloop_db():
    payload = {
        "pod_name": "user-service-71b69-pq912",
        "namespace": "users",
        "failure_type": "CrashLoopBackOff",
        "describe_output": "State: Waiting (CrashLoopBackOff)",
        "pod_logs": "psycopg.OperationalError: connection to server at '127.0.0.1', port 5432 failed: Connection refused",
    }
    response = client.post("/api/k8s/troubleshoot-pod", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Database Connection Refused" in data["detected_issue"]
    assert "initContainers" in data["yaml_patch"]
