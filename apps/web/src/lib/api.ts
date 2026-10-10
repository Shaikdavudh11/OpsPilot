import {
  HealthResponse,
  DemoScenario,
  IncidentAnalysisRequest,
  IncidentAnalysisResponse,
  SavedIncidentSummary,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

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
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      // Short cache or no-store for dynamic incident data
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
      err instanceof Error ? err.message : "Failed to connect to OpsPilot API";
    throw new ApiError(
      `Unable to reach OpsPilot API at ${API_BASE_URL}. Ensure the backend service is running. (${message})`
    );
  }
}

export const opsApi = {
  getHealth: () => request<HealthResponse>("/health"),
  getDemoScenarios: () => request<DemoScenario[]>("/api/demo-scenarios"),
  analyzeIncident: (data: IncidentAnalysisRequest) =>
    request<IncidentAnalysisResponse>("/api/incidents/analyze", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getIncidents: () => request<SavedIncidentSummary[]>("/api/incidents"),
  getIncidentById: (id: string) =>
    request<IncidentAnalysisResponse>(`/api/incidents/${id}`),
};
