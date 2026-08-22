"""Diagnosis orchestration service.

Coordinates the investigation pipeline: collects cluster evidence
and sends it to the AI SRE agent for reasoning.
"""

from typing import Any
from loguru import logger

from app.services.investigation import investigation_service
from app.ai.agent import kubernetes_agent
from app.services.realtime import realtime_service


class DiagnosisService:
    """Orchestrates Kubernetes investigation and AI diagnosis."""

    async def run_diagnosis(
        self,
        namespace: str | None = None,
        context: str | None = None,
        investigation_id: str | None = None,
    ) -> dict[str, Any]:
        """Run a full cluster investigation and produce an AI diagnosis."""
        logger.info("Executing full cluster diagnosis pipeline...")

        # Step 1: Collect Kubernetes cluster evidence
        investigation_data = await investigation_service.run_investigation(
            namespace=namespace, context=context, investigation_id=investigation_id
        )

        # Step 2: Feed evidence to the AI reasoning agent
        try:
            logger.info("Sending investigation evidence to AI Reasoning Agent...")
            await realtime_service.emit_progress(
                investigation_id, "✓ AI Reasoning"
            )
            diagnosis_data = await kubernetes_agent.analyze_cluster(investigation_data)
            await realtime_service.emit_progress(
                investigation_id, "Diagnosis complete"
            )
        except Exception as e:
            logger.error(f"AI diagnosis orchestration failed: {e}")
            diagnosis_data = {
                "root_cause": "Orchestration Error",
                "explanation": f"Failed to run diagnosis pipeline: {str(e)}",
                "fix": "Check backend application logs for details.",
                "kubectl_commands": [],
                "prevention": "Ensure backend services are healthy.",
                "confidence": 0,
                "confidence_reasoning": "Pipeline orchestration error.",
            }

        return {"investigation": investigation_data, "diagnosis": diagnosis_data}


diagnosis_service = DiagnosisService()
