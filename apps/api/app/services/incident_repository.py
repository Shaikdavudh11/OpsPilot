import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import IncidentModel
from app.schemas.incident import (
    IncidentAnalysisResponse,
    LikelyRootCause,
    EvidenceItem,
    RecommendationItem,
    PreventionItem,
    Severity,
)


class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_incident(
        self,
        analysis: IncidentAnalysisResponse,
        environment: str = "production",
        service_name: str = "unknown-service",
        raw_logs_snippet: str = "",
    ) -> IncidentModel:
        record = IncidentModel(
            id=analysis.id,
            title=analysis.title,
            environment=environment,
            service_name=service_name,
            severity=analysis.severity.value,
            summary=analysis.summary,
            likely_root_cause_json=analysis.likely_root_cause.model_dump_json(),
            evidence_json=json.dumps([e.model_dump() for e in analysis.evidence]),
            recommendations_json=json.dumps([r.model_dump() for r in analysis.recommendations]),
            prevention_json=json.dumps([p.model_dump() for p in analysis.prevention]),
            limitations_json=json.dumps(analysis.limitations),
            raw_logs_snippet=raw_logs_snippet[:1000] if raw_logs_snippet else "",
            redacted_secrets_count=analysis.redacted_secrets_count,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_incidents(self, limit: int = 50) -> List[dict]:
        records = (
            self.db.query(IncidentModel)
            .order_by(IncidentModel.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "title": r.title,
                "severity": r.severity,
                "summary": r.summary,
                "environment": r.environment,
                "service_name": r.service_name,
                "created_at": r.created_at.isoformat() if r.created_at else "",
            }
            for r in records
        ]

    def get_incident(self, incident_id: str) -> Optional[IncidentAnalysisResponse]:
        record = self.db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
        if not record:
            return None

        return IncidentAnalysisResponse(
            id=record.id,
            title=record.title,
            severity=Severity(record.severity),
            summary=record.summary,
            likely_root_cause=LikelyRootCause.model_validate_json(record.likely_root_cause_json),
            evidence=[EvidenceItem.model_validate(e) for e in json.loads(record.evidence_json)],
            recommendations=[
                RecommendationItem.model_validate(r) for r in json.loads(record.recommendations_json)
            ],
            prevention=[PreventionItem.model_validate(p) for p in json.loads(record.prevention_json)],
            limitations=json.loads(record.limitations_json),
            analyzed_at=record.created_at.isoformat() if record.created_at else "",
            redacted_secrets_count=record.redacted_secrets_count,
        )
