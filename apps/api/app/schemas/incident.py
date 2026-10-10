from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EvidenceItem(BaseModel):
    source: str = Field(
        ...,
        description="The log stream, component, or line reference where the evidence was found.",
        json_schema_extra={"example": "stderr / auth_service.log:L42"},
    )
    finding: str = Field(
        ...,
        description="Specific factual observation extracted directly from the logs.",
        json_schema_extra={"example": "Connection to database host db.internal:5432 refused repeatedly."},
    )


class RecommendationItem(BaseModel):
    action: str = Field(
        ...,
        description="Clear, actionable diagnostic or remediation step.",
        json_schema_extra={"example": "Verify PostgreSQL service status on db.internal."},
    )
    reason: str = Field(
        ...,
        description="Technical justification for taking this action.",
        json_schema_extra={"example": "Direct connection refused indicates the service daemon is not accepting sockets."},
    )
    risk_level: RiskLevel = Field(
        default=RiskLevel.LOW,
        description="Operational risk level of performing this diagnostic action.",
    )
    suggested_command: Optional[str] = Field(
        default=None,
        description="Optional diagnostic CLI command for operator inspection (never executed by the system).",
        json_schema_extra={"example": "systemctl status postgresql"},
    )


class PreventionItem(BaseModel):
    strategy: str = Field(
        ...,
        description="Systemic architectural, operational, or monitoring improvement.",
        json_schema_extra={"example": "Implement database connection pooling and retry backoff."},
    )
    details: str = Field(
        ...,
        description="Detailed implementation guidance for engineering teams.",
        json_schema_extra={"example": "Configure HikariCP or PgBouncer with circuit breaker to avoid cascading thread exhaustion."},
    )


class LikelyRootCause(BaseModel):
    description: str = Field(
        ...,
        description="Concise description of the primary root cause identified from the evidence.",
        json_schema_extra={"example": "Database port unreachable due to crashed daemon or misconfigured security group."},
    )
    confidence: Confidence = Field(
        default=Confidence.MEDIUM,
        description="Estimated confidence level based on log completeness.",
    )
    reasoning: str = Field(
        ...,
        description="Step-by-step reasoning linking the evidence to this root cause hypothesis.",
        json_schema_extra={"example": "Logs explicitly report ECONNREFUSED on port 5432 with 0 successful handshakes."},
    )


class IncidentAnalysisRequest(BaseModel):
    title: Optional[str] = Field(
        default="Uncategorized Incident",
        description="Optional title or brief incident summary.",
        max_length=200,
    )
    environment: Optional[str] = Field(
        default="production",
        description="Environment where incident occurred (e.g. production, staging, dev).",
        max_length=50,
    )
    service_name: Optional[str] = Field(
        default="unknown-service",
        description="Affected microservice or workload name.",
        max_length=100,
    )
    raw_logs: str = Field(
        ...,
        min_length=10,
        description="Raw error log output, stack trace, or incident evidence.",
    )


class IncidentAnalysisResponse(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="Unique identifier for this analysis record.",
    )
    title: str = Field(
        ...,
        description="Normalized incident title.",
    )
    severity: Severity = Field(
        ...,
        description="Assessed incident severity level.",
    )
    summary: str = Field(
        ...,
        description="High-level incident summary for engineers and responders.",
    )
    likely_root_cause: LikelyRootCause = Field(
        ...,
        description="Primary root cause assessment.",
    )
    evidence: List[EvidenceItem] = Field(
        default_factory=list,
        description="Factual evidence extracted directly from the provided logs.",
    )
    recommendations: List[RecommendationItem] = Field(
        default_factory=list,
        description="Prioritized diagnostic and remediation actions.",
    )
    prevention: List[PreventionItem] = Field(
        default_factory=list,
        description="Long-term prevention and hardening recommendations.",
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Identified uncertainties, uninspected systems, or missing log context.",
    )
    analyzed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of analysis completion.",
    )
    redacted_secrets_count: int = Field(
        default=0,
        description="Number of potential API keys, passwords, or tokens scrubbed before analysis.",
    )
