import pytest
from app.services.providers.mock import MockAIProvider
from app.schemas.incident import Severity, Confidence


@pytest.mark.asyncio
async def test_mock_provider_postgres_scenario():
    provider = MockAIProvider()
    logs = """
    2026-10-10 09:12:01.320 [error] django.db.utils.OperationalError: could not connect to server: Connection refused
    Is the server running on host "db.internal" (10.0.4.12) and accepting TCP/IP connections on port 5432?
    """

    res = await provider.analyze(
        sanitized_logs=logs,
        title="DB connection failure",
        environment="production",
        service_name="payment-service",
    )

    assert res.severity == Severity.HIGH
    assert "PostgreSQL" in res.title or "database" in res.summary.lower()
    assert res.likely_root_cause.confidence == Confidence.HIGH
    assert len(res.evidence) > 0
    assert any("5432" in e.finding for e in res.evidence)
    assert len(res.recommendations) >= 2
    assert any(r.suggested_command is not None for r in res.recommendations)
    assert len(res.limitations) > 0


@pytest.mark.asyncio
async def test_mock_provider_k8s_crashloop_scenario():
    provider = MockAIProvider()
    logs = """
    pod/auth-svc-765f8-qwert: Back-off restarting failed container auth-svc in pod auth-svc-765f8-qwert_default
    Last State: Terminated with exit code 137, Reason: OOMKilled
    """

    res = await provider.analyze(
        sanitized_logs=logs,
        title="Auth service crash",
        environment="production",
        service_name="auth-service",
    )

    assert res.severity in [Severity.HIGH, Severity.CRITICAL]
    assert "OOM" in res.summary or "memory" in res.likely_root_cause.description.lower()
    assert len(res.recommendations) > 0
