from pydantic import BaseModel, Field
from app.schemas.incident import Severity


class DemoScenario(BaseModel):
    id: str = Field(..., description="Unique scenario slug or identifier.")
    title: str = Field(..., description="Human-readable scenario title.")
    description: str = Field(..., description="Brief scenario operational context.")
    category: str = Field(..., description="System category (e.g. Database, Kubernetes, Docker, CI/CD, Application).")
    environment: str = Field(default="production", description="Associated environment.")
    service_name: str = Field(default="core-service", description="Workload or service name.")
    expected_severity: Severity = Field(..., description="Expected incident severity.")
    raw_logs: str = Field(..., description="Realistic raw log output reflecting this failure.")
