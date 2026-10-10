import pytest
from pydantic import ValidationError
from app.schemas.incident import (
    IncidentAnalysisRequest,
    IncidentAnalysisResponse,
    Severity,
    LikelyRootCause,
    EvidenceItem,
    RecommendationItem,
    PreventionItem,
    RiskLevel,
    Confidence,
)


def test_incident_request_validation():
    # Valid minimal payload
    req = IncidentAnalysisRequest(raw_logs="error: connection refused on port 5432")
    assert req.raw_logs == "error: connection refused on port 5432"
    assert req.title == "Uncategorized Incident"
    assert req.environment == "production"

    # Too short raw_logs should fail validation (min_length=10)
    with pytest.raises(ValidationError):
        IncidentAnalysisRequest(raw_logs="short")


def test_incident_response_validation():
    res = IncidentAnalysisResponse(
        title="PostgreSQL Down",
        severity=Severity.HIGH,
        summary="Database unreachable",
        likely_root_cause=LikelyRootCause(
            description="Daemon killed",
            confidence=Confidence.HIGH,
            reasoning="Connection refused",
        ),
        evidence=[
            EvidenceItem(source="app.log", finding="ECONNREFUSED 127.0.0.1:5432")
        ],
        recommendations=[
            RecommendationItem(
                action="Restart postgres",
                reason="Restore service",
                risk_level=RiskLevel.LOW,
                suggested_command="systemctl restart postgresql",
            )
        ],
        prevention=[
            PreventionItem(
                strategy="Add watchdog",
                details="Restart daemon automatically",
            )
        ],
        limitations=["No syslog access"],
    )

    assert res.severity == Severity.HIGH
    assert len(res.evidence) == 1
    assert res.recommendations[0].suggested_command == "systemctl restart postgresql"
