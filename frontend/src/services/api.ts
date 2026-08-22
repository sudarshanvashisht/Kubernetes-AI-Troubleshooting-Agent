import axios from "axios";
import type { FullDiagnosisResponse } from "../types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 120000, // 2 minutes for diagnosis LLM pipeline
});

/**
 * Check backend health status.
 */
export async function checkHealth(): Promise<{ status: string }> {
  const response = await apiClient.get("/health");
  return response.data;
}

/**
 * Fetch available Kubernetes clusters from backend.
 */
export async function getClusters(): Promise<{ clusters: string[]; current_context?: string }> {
  try {
    const response = await apiClient.get("/clusters");
    return response.data;
  } catch {
    return { clusters: ["kind-tws-cluster"], current_context: "kind-tws-cluster" };
  }
}

/**
 * Trigger cluster investigation and diagnosis pipeline.
 */
export async function investigateCluster(
  investigationId?: string,
  namespace?: string,
  context?: string
): Promise<FullDiagnosisResponse> {
  const payload: Record<string, string | undefined> = {};
  if (investigationId) {
    payload.investigation_id = investigationId;
  }
  if (namespace && namespace.trim().length > 0) {
    payload.namespace = namespace.trim();
  }
  if (context && context.trim().length > 0) {
    payload.context = context.trim();
  }

  const response = await apiClient.post<FullDiagnosisResponse>(
    "/investigate",
    payload
  );
  return response.data;
}
