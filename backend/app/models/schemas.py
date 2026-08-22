"""Pydantic models for request/response schemas."""

from pydantic import BaseModel
from typing import Optional, Any


class DiagnosisRequest(BaseModel):
    """Request model for triggering a cluster diagnosis."""

    namespace: Optional[str] = None
    context: Optional[str] = None
    resource_type: Optional[str] = None
    resource_name: Optional[str] = None
    investigation_id: Optional[str] = None


class DiagnosisResponse(BaseModel):
    """Response model for a cluster diagnosis result."""

    status: str
    root_cause: Optional[str] = None
    suggestions: list[str] = []
    raw_data: Optional[dict] = None


# --- Investigation Models ---


class ProblematicPod(BaseModel):
    """A pod with issues detected during inspection."""

    name: str
    namespace: str
    status: str
    message: str = ""
    restart_count: int = 0


class PodInvestigation(BaseModel):
    """Result of pod inspection."""

    healthy: bool
    total_pods: int = 0
    problematic_pods: list[ProblematicPod] = []
    error: Optional[str] = None


class LogEntry(BaseModel):
    """Log output from a single pod."""

    pod_name: str
    namespace: str
    logs: str = ""
    source: Optional[str] = None
    error: Optional[str] = None


class WarningEvent(BaseModel):
    """A Kubernetes warning event."""

    reason: str
    message: str = ""
    namespace: str = ""
    involved_object: dict = {}
    count: int = 1
    last_timestamp: str = ""


class EventInvestigation(BaseModel):
    """Result of events analysis."""

    total_events: int = 0
    warning_events: list[WarningEvent] = []
    has_issues: bool = False
    error: Optional[str] = None


class UnhealthyDeployment(BaseModel):
    """A deployment with issues."""

    name: str
    namespace: str
    desired: int = 0
    available: int = 0
    unavailable: int = 0
    conditions: list[dict] = []


class DeploymentInvestigation(BaseModel):
    """Result of deployment inspection."""

    healthy: bool
    total_deployments: int = 0
    unhealthy_deployments: list[UnhealthyDeployment] = []
    error: Optional[str] = None


class ProblematicService(BaseModel):
    """A service with networking issues."""

    name: str
    namespace: str
    type: str = "ClusterIP"
    issues: list[str] = []


class NetworkInvestigation(BaseModel):
    """Result of network inspection."""

    total_services: int = 0
    problematic_services: list[ProblematicService] = []
    has_issues: bool = False
    error: Optional[str] = None


class InvestigationResult(BaseModel):
    """Combined results from all investigation steps."""

    pods: PodInvestigation = PodInvestigation(healthy=True)
    logs: list[LogEntry] = []
    events: EventInvestigation = EventInvestigation()
    deployments: DeploymentInvestigation = DeploymentInvestigation(healthy=True)
    network: NetworkInvestigation = NetworkInvestigation()


class InvestigationRequest(BaseModel):
    """Request model for triggering an investigation."""

    namespace: Optional[str] = None
    context: Optional[str] = None
    investigation_id: Optional[str] = None


class InvestigationResponse(BaseModel):
    """Response model for an investigation result."""

    status: str
    investigation: InvestigationResult


# --- AI Diagnosis Models ---


class AIDiagnosis(BaseModel):
    """AI SRE analysis response schema."""

    root_cause: str
    explanation: str
    fix: str
    kubectl_commands: list[str] = []
    prevention: str
    confidence: int
    confidence_reasoning: str = ""


class FullDiagnosisResponse(BaseModel):
    """Response model containing investigation data and AI diagnosis."""

    status: str
    investigation: InvestigationResult
    diagnosis: Optional[AIDiagnosis] = None
