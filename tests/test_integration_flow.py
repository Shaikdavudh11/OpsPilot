import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add apps/api to PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "api"))

from app.main import app

client = TestClient(app)


def test_full_e2e_incident_lifecycle():
    # 1. Health check
    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    # 2. Get demo scenarios
    scenarios_res = client.get("/api/demo-scenarios")
    assert scenarios_res.status_code == 200
    scenarios = scenarios_res.json()
    assert len(scenarios) == 6

    # 3. Analyze each demo scenario and verify full schema compliance
    created_ids = []
    for sc in scenarios:
        req_payload = {
            "title": sc["title"],
            "environment": sc["environment"],
            "service_name": sc["service_name"],
            "raw_logs": sc["raw_logs"],
        }
        res = client.post("/api/incidents/analyze", json=req_payload)
        assert res.status_code == 200, f"Failed analyzing scenario {sc['id']}"
        data = res.json()

        assert data["id"] is not None
        assert data["severity"] in ["low", "medium", "high", "critical"]
        assert len(data["evidence"]) > 0
        assert len(data["recommendations"]) > 0
        assert data["likely_root_cause"]["confidence"] in ["low", "medium", "high"]
        assert isinstance(data["limitations"], list)
        created_ids.append(data["id"])

    # 4. Verify list incidents contains all newly analyzed incidents
    list_res = client.get("/api/incidents")
    assert list_res.status_code == 200
    all_saved = list_res.json()
    all_saved_ids = [item["id"] for item in all_saved]
    for cid in created_ids:
        assert cid in all_saved_ids

    # 5. Verify single incident retrieval
    single_res = client.get(f"/api/incidents/{created_ids[0]}")
    assert single_res.status_code == 200
    single_data = single_res.json()
    assert single_data["id"] == created_ids[0]
