from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_demo_scenarios():
    response = client.get("/api/demo-scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    assert len(scenarios) >= 6

    # Verify key properties of scenarios
    scenario_ids = [s["id"] for s in scenarios]
    assert "postgres-conn-refused" in scenario_ids
    assert "docker-startup-exit" in scenario_ids
    assert "k8s-crashloop-oom" in scenario_ids
    assert "k8s-imagepull-backoff" in scenario_ids
    assert "ci-test-failure" in scenario_ids
    assert "app-http-500" in scenario_ids

    for sc in scenarios:
        assert len(sc["raw_logs"]) > 20
        assert sc["expected_severity"] in ["low", "medium", "high", "critical"]
