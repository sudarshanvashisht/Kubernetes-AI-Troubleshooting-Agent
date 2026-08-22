"""Investigation orchestration service.

Coordinates all Kubernetes inspection modules to collect
troubleshooting evidence in a structured pipeline.
"""

from loguru import logger

from app.kubernetes.inspector import pod_inspector
from app.kubernetes.logs_collector import logs_collector
from app.kubernetes.events_analyzer import events_analyzer
from app.kubernetes.deployment_inspector import deployment_inspector
from app.kubernetes.network_inspector import network_inspector
from app.services.realtime import realtime_service


class InvestigationService:
    """Orchestrates the full Kubernetes investigation pipeline."""

    async def run_investigation(
        self,
        namespace: str | None = None,
        context: str | None = None,
        investigation_id: str | None = None,
    ) -> dict:
        """Run a complete cluster investigation."""
        logger.info("Starting cluster investigation...")

        results = {
            "pods": {},
            "logs": [],
            "events": {},
            "deployments": {},
            "network": {},
        }

        # Step 1: Check Pods
        try:
            logger.info("Step 1/5: Checking Pods...")
            await realtime_service.emit_progress(investigation_id, "✓ Checking Pods")
            results["pods"] = await pod_inspector.inspect_pods(namespace, context=context)
        except Exception as e:
            logger.error(f"Pod inspection failed: {e}")
            results["pods"] = {
                "healthy": False,
                "total_pods": 0,
                "problematic_pods": [],
                "error": str(e),
            }

        # Step 2: Reading Logs for problematic pods
        try:
            logger.info("Step 2/5: Reading Logs...")
            await realtime_service.emit_progress(investigation_id, "✓ Reading Logs")
            problematic_pods = results["pods"].get("problematic_pods", [])
            if problematic_pods:
                results["logs"] = await logs_collector.collect_failed_pod_logs(
                    problematic_pods, context=context
                )
            else:
                logger.info("No problematic pods found, skipping log collection")
        except Exception as e:
            logger.error(f"Log collection failed: {e}")
            results["logs"] = []

        # Step 3: Analyze Events
        try:
            logger.info("Step 3/5: Analyzing Events...")
            await realtime_service.emit_progress(investigation_id, "✓ Analyzing Events")
            results["events"] = await events_analyzer.analyze_events(namespace, context=context)
        except Exception as e:
            logger.error(f"Events analysis failed: {e}")
            results["events"] = {
                "total_events": 0,
                "warning_events": [],
                "has_issues": False,
                "error": str(e),
            }

        # Step 4: Inspect Deployments
        try:
            logger.info("Step 4/5: Inspecting Deployments...")
            await realtime_service.emit_progress(
                investigation_id, "✓ Inspecting Deployments"
            )
            results["deployments"] = await deployment_inspector.inspect_deployments(
                namespace, context=context
            )
        except Exception as e:
            logger.error(f"Deployment inspection failed: {e}")
            results["deployments"] = {
                "healthy": False,
                "total_deployments": 0,
                "unhealthy_deployments": [],
                "error": str(e),
            }

        # Step 5: Check Networking
        try:
            logger.info("Step 5/5: Checking Networking...")
            await realtime_service.emit_progress(
                investigation_id, "✓ Checking Networking"
            )
            results["network"] = await network_inspector.inspect_services(namespace, context=context)
        except Exception as e:
            logger.error(f"Network inspection failed: {e}")
            results["network"] = {
                "total_services": 0,
                "problematic_services": [],
                "has_issues": False,
                "error": str(e),
            }

        logger.info("Cluster investigation complete")
        return results


# Shared instance
investigation_service = InvestigationService()
