import type { UserSchema } from "@insforge/sdk";

export type AuthUser = UserSchema;

/**
 * Request model for triggering a cluster diagnosis.
 */
export interface DiagnosisRequest {
  namespace?: string;
  investigation_id?: string;
  resource_type?: string;
  resource_name?: string;
}

/**
 * Pod inspection models
 */
export interface ProblematicPod {
  name: string;
  namespace: string;
  status: string;
  message?: string;
  restart_count?: number;
}

export interface PodInvestigation {
  healthy: boolean;
  total_pods: number;
  problematic_pods: ProblematicPod[];
  error?: string | null;
}

/**
 * Log collection model
 */
export interface LogEntry {
  pod_name: string;
  namespace: string;
  logs: string;
  source?: string | null;
  error?: string | null;
}

/**
 * Event analysis models
 */
export interface WarningEvent {
  reason: string;
  message: string;
  namespace: string;
  involved_object?: Record<string, unknown>;
  count?: number;
  last_timestamp?: string;
}

export interface EventInvestigation {
  total_events: number;
  warning_events: WarningEvent[];
  has_issues: boolean;
  error?: string | null;
}

/**
 * Deployment inspection models
 */
export interface UnhealthyDeployment {
  name: string;
  namespace: string;
  desired: number;
  available: number;
  unavailable: number;
  conditions?: Array<Record<string, unknown>>;
}

export interface DeploymentInvestigation {
  healthy: boolean;
  total_deployments: number;
  unhealthy_deployments: UnhealthyDeployment[];
  error?: string | null;
}

/**
 * Network inspection models
 */
export interface ProblematicService {
  name: string;
  namespace: string;
  type: string;
  issues: string[];
}

export interface NetworkInvestigation {
  total_services: number;
  problematic_services: ProblematicService[];
  has_issues: boolean;
  error?: string | null;
}

/**
 * Combined results from all investigation steps.
 */
export interface InvestigationResult {
  pods?: PodInvestigation;
  logs?: LogEntry[];
  events?: EventInvestigation;
  deployments?: DeploymentInvestigation;
  network?: NetworkInvestigation;
}

/**
 * AI SRE diagnosis schema
 */
export interface AIDiagnosis {
  root_cause: string;
  explanation: string;
  fix: string;
  kubectl_commands?: string[];
  prevention?: string;
  confidence: number;
  confidence_reasoning?: string;
}

/**
 * Full backend diagnosis response
 */
export interface FullDiagnosisResponse {
  status: "success" | "error" | string;
  investigation?: InvestigationResult;
  diagnosis?: AIDiagnosis | null;
  root_cause?: string;
  suggestions?: string[];
  confidence?: number;
  rawData?: Record<string, unknown>;
}

/**
 * Investigation record saved in database / local history
 */
export interface InvestigationHistoryRecord {
  id: string;
  user_id?: string;
  created_at?: string;
  result: FullDiagnosisResponse;
}

/**
 * Realtime progress notification payload
 */
export interface RealtimeProgressPayload {
  message?: string;
  step?: number;
  totalSteps?: number;
  timestamp?: string;
  [key: string]: unknown;
}
