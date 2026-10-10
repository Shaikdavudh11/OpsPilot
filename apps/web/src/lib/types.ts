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
