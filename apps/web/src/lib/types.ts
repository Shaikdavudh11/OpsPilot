export type Severity = "low" | "medium" | "high" | "critical";
export type RiskLevel = "low" | "medium" | "high";
export type Confidence = "low" | "medium" | "high";

export interface EvidenceItem {
  source: string;
  finding: string;
}

export interface RecommendationItem {
  action: string;
  reason: string;
  risk_level: RiskLevel;
  suggested_command?: string | null;
}

export interface PreventionItem {
  strategy: string;
  details: string;
}

export interface LikelyRootCause {
  description: string;
  confidence: Confidence;
  reasoning: string;
}

export interface IncidentAnalysisResponse {
  id?: string;
  title: string;
  severity: Severity;
  summary: string;
  likely_root_cause: LikelyRootCause;
  evidence: EvidenceItem[];
  recommendations: RecommendationItem[];
  prevention: PreventionItem[];
  limitations: string[];
  analyzed_at?: string;
  redacted_secrets_count?: number;
}

export interface IncidentAnalysisRequest {
  title?: string;
  environment?: string;
  service_name?: string;
  raw_logs: string;
}

export interface DemoScenario {
  id: string;
  title: string;
  description: string;
  category: string;
  environment: string;
  service_name: string;
  expected_severity: Severity;
  raw_logs: string;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
  ai_provider: string;
  timestamp: string;
}

export interface SavedIncidentSummary {
  id: string;
  title: string;
  severity: Severity;
  summary: string;
  environment: string;
  service_name: string;
  created_at: string;
}

// ==========================================
// Kubernetes Agent & Copilot Types
// ==========================================

export interface RepoAnalysisRequest {
  repo_source: "github" | "local";
  repo_url?: string;
  local_path?: string;
  branch?: string;
  app_name?: string;
  target_port?: number;
  namespace?: string;
}

export interface DetectedStack {
  primary_language: string;
  framework: string;
  build_tool?: string | null;
  detected_ports: number[];
  recommended_port: number;
  has_dockerfile: boolean;
  has_existing_k8s: boolean;
  detected_env_vars: string[];
  backing_services: string[];
  health_endpoint: string;
  package_files_found: string[];
  total_files_scanned: number;
}

export interface GeneratedManifests {
  dockerfile: string;
  deployment_yaml: string;
  service_yaml: string;
  configmap_yaml: string;
  secret_yaml: string;
  ingress_yaml: string;
  hpa_yaml: string;
  all_in_one_yaml: string;
}

export interface DeploymentStep {
  step_number: number;
  title: string;
  description: string;
  commands: string[];
  verification?: string | null;
}

export interface K8sAnalysisResponse {
  app_name: string;
  namespace: string;
  repo_source: string;
  repo_reference: string;
  detected_stack: DetectedStack;
  manifests: GeneratedManifests;
  deployment_steps: DeploymentStep[];
  production_recommendations: string[];
  security_hardening: string[];
}

export interface PodTroubleshootRequest {
  pod_name?: string;
  namespace?: string;
  failure_type?: string;
  describe_output?: string;
  pod_logs?: string;
  current_manifest?: string;
}

export interface PodTroubleshootResponse {
  pod_name: string;
  namespace: string;
  detected_issue: string;
  root_cause: string;
  confidence: "low" | "medium" | "high";
  evidence: string[];
  remediation_summary: string;
  yaml_patch?: string | null;
  recommended_commands: string[];
  preventative_guidance: string[];
}

export interface SampleRepo {
  id: string;
  name: string;
  description: string;
  repo_source: "github" | "local";
  repo_url?: string;
  local_path?: string;
  language: string;
  framework: string;
  sample_pod_issues?: Array<{
    title: string;
    failure_type: string;
    describe_output: string;
    pod_logs: string;
  }>;
}
