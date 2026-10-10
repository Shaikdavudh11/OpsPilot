import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_incident_persistence_and_retrieval():
    # 1. Post a new incident
    payload = {
        "title": "Persistent Postgres Incident Test",
        "environment": "staging",
        "service_name": "order-api",
        "raw_logs": "ERROR: Connection refused on port 5432 to postgres server db.staging.internal",
    }
    analyze_resp = client.post("/api/incidents/analyze", json=payload)
    assert analyze_resp.status_code == 200
    analyzed_data = analyze_resp.json()
    incident_id = analyzed_data["id"]
    assert incident_id is not None

    # 2. List incidents and verify it is present
    list_resp = client.get("/api/incidents")
    assert list_resp.status_code == 200
    incidents = list_resp.json()
    matching = [i for i in incidents if i["id"] == incident_id]
    assert len(matching) == 1
    assert matching[0]["title"] == "Persistent Postgres Incident Test"
    assert matching[0]["service_name"] == "order-api"

    # 3. Fetch single incident by ID
    get_resp = client.get(f"/api/incidents/{incident_id}")
    assert get_resp.status_code == 200
    fetched_data = get_resp.json()
    assert fetched_data["id"] == incident_id
    assert fetched_data["title"] == "Persistent Postgres Incident Test"
    assert len(fetched_data["evidence"]) > 0
    assert len(fetched_data["recommendations"]) > 0

    # 4. Non-existent ID returns 404
    not_found_resp = client.get("/api/incidents/00000000-0000-0000-0000-000000000000")
    assert not_found_resp.status_code == 404
