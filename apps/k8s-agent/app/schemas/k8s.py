from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class RepoAnalysisRequest(BaseModel):
    repo_source: str = Field(..., description="'github' or 'local'")
    repo_url: Optional[str] = Field(None, description="GitHub or Git repository URL (e.g., https://github.com/owner/repo)")
    local_path: Optional[str] = Field(None, description="Absolute or relative local folder path")
    branch: Optional[str] = Field("main", description="Git branch to analyze")
    app_name: Optional[str] = Field(None, description="Custom application name for Kubernetes resources")
    target_port: Optional[int] = Field(None, description="Override container exposed port if known")
    namespace: Optional[str] = Field("default", description="Target Kubernetes namespace")


class DetectedStack(BaseModel):
    primary_language: str
    framework: str
    build_tool: Optional[str] = None
    detected_ports: List[int] = []
    recommended_port: int = 8080
    has_dockerfile: bool = False
    has_existing_k8s: bool = False
    detected_env_vars: List[str] = []
    backing_services: List[str] = []
    health_endpoint: str = "/health"
    package_files_found: List[str] = []
    total_files_scanned: int = 0


class GeneratedManifests(BaseModel):
    dockerfile: str
    deployment_yaml: str
    service_yaml: str
    configmap_yaml: str
    secret_yaml: str
    ingress_yaml: str
    hpa_yaml: str
    all_in_one_yaml: str


class DeploymentStep(BaseModel):
    step_number: int
    title: str
    description: str
    commands: List[str]
    verification: Optional[str] = None


class K8sAnalysisResponse(BaseModel):
    app_name: str
    namespace: str
    repo_source: str
    repo_reference: str
    detected_stack: DetectedStack
    manifests: GeneratedManifests
    deployment_steps: List[DeploymentStep]
    production_recommendations: List[str]
    security_hardening: List[str]


class PodTroubleshootRequest(BaseModel):
    pod_name: Optional[str] = "app-pod-xyz"
    namespace: Optional[str] = "default"
    failure_type: Optional[str] = None
    describe_output: Optional[str] = Field(None, description="kubectl describe pod output or events")
    pod_logs: Optional[str] = Field(None, description="Raw container logs / stacktrace")
    current_manifest: Optional[str] = Field(None, description="Existing deployment or pod YAML if available")


class PodTroubleshootResponse(BaseModel):
    pod_name: str
    namespace: str
    detected_issue: str
    root_cause: str
    confidence: str
    evidence: List[str]
    remediation_summary: str
    yaml_patch: Optional[str] = None
    recommended_commands: List[str]
    preventative_guidance: List[str]


class SampleRepo(BaseModel):
    id: str
    name: str
    description: str
    repo_source: str
    repo_url: Optional[str] = None
    local_path: Optional[str] = None
    language: str
    framework: str
    sample_pod_issues: List[Dict[str, Any]] = []


class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "OpsPilot Kubernetes Agent API"
    version: str = "1.0.0"
    environment: str = "development"
    port: int = 8002
