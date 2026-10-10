import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="Uncategorized Incident")
    environment = Column(String(64), nullable=False, default="production")
    service_name = Column(String(128), nullable=False, default="unknown-service")
    severity = Column(String(32), nullable=False)
    summary = Column(Text, nullable=False)

    # JSON-serialized fields
    likely_root_cause_json = Column(Text, nullable=False)
    evidence_json = Column(Text, nullable=False, default="[]")
    recommendations_json = Column(Text, nullable=False, default="[]")
    prevention_json = Column(Text, nullable=False, default="[]")
    limitations_json = Column(Text, nullable=False, default="[]")

    raw_logs_snippet = Column(Text, nullable=True)
    redacted_secrets_count = Column(Integer, default=0)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
