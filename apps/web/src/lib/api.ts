import {
  HealthResponse,
  DemoScenario,
  IncidentAnalysisRequest,
  IncidentAnalysisResponse,
  SavedIncidentSummary,
  RepoAnalysisRequest,
  K8sAnalysisResponse,
  PodTroubleshootRequest,
  PodTroubleshootResponse,
  SampleRepo,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
const K8S_API_BASE_URL =
  process.env.NEXT_PUBLIC_K8S_API_URL || "http://localhost:8002";

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  baseUrl: string = API_BASE_URL
): Promise<T> {
  const url = `${baseUrl}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      cache: "no-store",
    });

    if (!response.ok) {
      let errorMessage = `API request failed with status ${response.status}`;
      let errorDetails: unknown = null;
      try {
        const errorJson = await response.json();
        errorMessage = errorJson.detail || errorJson.message || errorMessage;
        errorDetails = errorJson;
      } catch {
        // Response was not JSON
      }
      throw new ApiError(errorMessage, response.status, errorDetails);
    }

    return (await response.json()) as T;
  } catch (err: unknown) {
    if (err instanceof ApiError) {
      throw err;
    }
    const message =
      err instanceof Error ? err.message : "Failed to connect to backend service";
    throw new ApiError(
      `Unable to reach service at ${baseUrl}. Ensure the service is running. (${message})`
    );
  }
}

export const opsApi = {
  // Incident Assistant (API Service - Port 8001)
  getHealth: () => request<HealthResponse>("/health", {}, API_BASE_URL),
  getDemoScenarios: () => request<DemoScenario[]>("/api/demo-scenarios", {}, API_BASE_URL),
  analyzeIncident: (data: IncidentAnalysisRequest) =>
    request<IncidentAnalysisResponse>("/api/incidents/analyze", {
      method: "POST",
      body: JSON.stringify(data),
    }, API_BASE_URL),
  getIncidents: () => request<SavedIncidentSummary[]>("/api/incidents", {}, API_BASE_URL),
  getIncidentById: (id: string) =>
    request<IncidentAnalysisResponse>(`/api/incidents/${id}`, {}, API_BASE_URL),

  // Autonomous Kubernetes Agent & Copilot (K8s Service - Port 8002)
  getK8sHealth: () => request<HealthResponse>("/health", {}, K8S_API_BASE_URL),
  analyzeRepo: (data: RepoAnalysisRequest) =>
    request<K8sAnalysisResponse>("/api/k8s/analyze-repo", {
      method: "POST",
      body: JSON.stringify(data),
    }, K8S_API_BASE_URL),
  troubleshootPod: (data: PodTroubleshootRequest) =>
    request<PodTroubleshootResponse>("/api/k8s/troubleshoot-pod", {
      method: "POST",
      body: JSON.stringify(data),
    }, K8S_API_BASE_URL),
  getK8sSampleRepos: () => request<SampleRepo[]>("/api/k8s/sample-repos", {}, K8S_API_BASE_URL),
};
