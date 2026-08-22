"""Deployment inspection utilities.

Inspects deployment status across the cluster, checking for
unavailable replicas, rollout failures, and unhealthy conditions.
"""

import json
from typing import Any

from loguru import logger

from app.kubernetes.kubectl import kubectl


class DeploymentInspector:
    """Inspects deployment health across the Kubernetes cluster."""

    async def inspect_deployments(
        self, namespace: str | None = None, context: str | None = None
    ) -> dict[str, Any]:
        """Inspect deployment status across the cluster.

        Args:
            namespace: Optional namespace filter. If None, checks all namespaces.
            context: Optional Kubernetes context.

        Returns:
            Dict with healthy status, total count, and unhealthy deployments list.
        """
        cmd = "get deployments -o json"
        if namespace:
            cmd += f" -n {namespace}"
        else:
            cmd += " -A"

        result = await kubectl.run(cmd, context=context)

        if not result.success:
            logger.error(f"Failed to get deployments: {result.stderr}")
            return {
                "healthy": False,
                "total_deployments": 0,
                "unhealthy_deployments": [],
                "error": result.stderr,
            }

        try:
            deployments_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse deployment data: {e}")
            return {
                "healthy": False,
                "total_deployments": 0,
                "unhealthy_deployments": [],
                "error": f"Failed to parse kubectl output: {e}",
            }

        deployments = deployments_data.get("items", [])
        unhealthy = []

        for deployment in deployments:
            dep_info = self._check_deployment_health(deployment)
            if dep_info:
                unhealthy.append(dep_info)

        healthy = len(unhealthy) == 0

        logger.info(
            f"Deployment inspection complete: {len(deployments)} total, "
            f"{len(unhealthy)} unhealthy"
        )

        return {
            "healthy": healthy,
            "total_deployments": len(deployments),
            "unhealthy_deployments": unhealthy,
        }

    def _check_deployment_health(self, deployment: dict) -> dict | None:
        """Check if a deployment is unhealthy.

        Returns deployment info dict if unhealthy, None if healthy.
        """
        metadata = deployment.get("metadata", {})
        spec = deployment.get("spec", {})
        status = deployment.get("status", {})

        name = metadata.get("name", "unknown")
        namespace = metadata.get("namespace", "default")
        desired = spec.get("replicas", 0)
        available = status.get("availableReplicas", 0) or 0
        unavailable = status.get("unavailableReplicas", 0) or 0

        # Extract conditions
        conditions = []
        for condition in status.get("conditions", []):
            if condition.get("status") != "True":
                conditions.append({
                    "type": condition.get("type", ""),
                    "status": condition.get("status", ""),
                    "reason": condition.get("reason", ""),
                    "message": condition.get("message", ""),
                })

        # Deployment is unhealthy if replicas are unavailable or conditions are bad
        if unavailable > 0 or available < desired or len(conditions) > 0:
            return {
                "name": name,
                "namespace": namespace,
                "desired": desired,
                "available": available,
                "unavailable": unavailable,
                "conditions": conditions,
            }

        return None


# Shared instance
deployment_inspector = DeploymentInspector()
