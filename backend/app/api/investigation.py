"""Investigation and Diagnosis API endpoints."""

from fastapi import APIRouter
from loguru import logger

from app.models.schemas import InvestigationRequest, FullDiagnosisResponse, InvestigationResult, AIDiagnosis
from app.services.diagnosis import diagnosis_service

router = APIRouter(tags=["Investigation"])


@router.post("/investigate", response_model=FullDiagnosisResponse)
async def investigate_cluster(request: InvestigationRequest = InvestigationRequest()):
    """Run a Kubernetes cluster investigation and AI diagnosis.

    Collects troubleshooting evidence from the cluster including:
    - Pod health status
    - Logs from problematic pods
    - Warning events
    - Deployment health
    - Network/service status

    Then, sends this evidence to the AI Site Reliability Engineer (SRE)
    to perform root cause analysis, generate recommended fixes, and assign
    a confidence rating.
    """
    logger.info(f"Full diagnosis requested (namespace={request.namespace})")

    try:
        pipeline_data = await diagnosis_service.run_diagnosis(
            namespace=request.namespace,
            context=request.context,
            investigation_id=request.investigation_id,
        )

        return FullDiagnosisResponse(
            status="success",
            investigation=InvestigationResult(**pipeline_data["investigation"]),
            diagnosis=AIDiagnosis(**pipeline_data["diagnosis"])
        )
    except Exception as e:
        logger.error(f"Diagnosis endpoint handler failed: {e}")
        return FullDiagnosisResponse(
            status="error",
            investigation=InvestigationResult(),
            diagnosis=AIDiagnosis(
                root_cause="Endpoint handler failed",
                explanation=str(e),
                fix="Check backend server logs.",
                kubectl_commands=[],
                prevention="Verify API endpoint health.",
                confidence=0,
                confidence_reasoning="Exception in endpoint handler."
            )
        )
