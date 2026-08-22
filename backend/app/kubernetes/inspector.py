"""Pod inspection utilities.

Inspects pod status across the cluster and detects unhealthy pods
such as CrashLoopBackOff, ImagePullBackOff, Pending, Error, OOMKilled,
and stuck ContainerCreating.
"""

import json
from typing import Any

from loguru import logger

from app.kubernetes.kubectl import kubectl


# Pod statuses considered problematic
PROBLEMATIC_STATUSES = {
    "CrashLoopBackOff",
    "ImagePullBackOff",
    "ErrImagePull",
    "Pending",
    "Error",
    "OOMKilled",
    "ContainerCreating",
    "CreateContainerConfigError",
    "InvalidImageName",
    "RunContainerError",
}


class PodInspector:
    """Inspects pod health across the Kubernetes cluster."""

    async def inspect_pods(
        self, namespace: str | None = None, context: str | None = None
    ) -> dict[str, Any]:
        """Get pod status across the cluster.

        Args:
            namespace: Optional namespace filter. If None, checks all namespaces.
            context: Optional Kubernetes context.

        Returns:
            Dict with healthy status, total pod count, and problematic pods list.
        """
        cmd = "get pods -o json"
        if namespace:
            cmd += f" -n {namespace}"
        else:
            cmd += " -A"

        result = await kubectl.run(cmd, context=context)

        if not result.success:
            logger.error(f"Failed to get pods: {result.stderr}")
            return {
                "healthy": False,
                "total_pods": 0,
                "problematic_pods": [],
                "error": result.stderr,
            }

        try:
            pods_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse pod data: {e}")
            return {
                "healthy": False,
                "total_pods": 0,
                "problematic_pods": [],
                "error": f"Failed to parse kubectl output: {e}",
            }

        pods = pods_data.get("items", [])
        problematic_pods = []

        for pod in pods:
            pod_info = self._check_pod_health(pod)
            if pod_info:
                problematic_pods.append(pod_info)

        healthy = len(problematic_pods) == 0

        logger.info(
            f"Pod inspection complete: {len(pods)} total, "
            f"{len(problematic_pods)} problematic"
        )

        return {
            "healthy": healthy,
            "total_pods": len(pods),
            "problematic_pods": problematic_pods,
        }

    def _check_pod_health(self, pod: dict) -> dict | None:
        """Check if a single pod is unhealthy.

        Returns pod info dict if unhealthy, None if healthy.
        """
        metadata = pod.get("metadata", {})
        status = pod.get("status", {})
        pod_name = metadata.get("name", "unknown")
        namespace = metadata.get("namespace", "default")
        phase = status.get("phase", "Unknown")

        # Check container statuses for issues
        container_statuses = status.get("containerStatuses", [])
        init_container_statuses = status.get("initContainerStatuses", [])

        for cs in container_statuses + init_container_statuses:
            # Check waiting state
            waiting = cs.get("state", {}).get("waiting", {})
            if waiting:
                reason = waiting.get("reason", "")
                if reason in PROBLEMATIC_STATUSES:
                    return {
                        "name": pod_name,
                        "namespace": namespace,
                        "status": reason,
                        "message": waiting.get("message", ""),
                        "restart_count": cs.get("restartCount", 0),
                    }

            # Check terminated state for OOMKilled
            terminated = cs.get("state", {}).get("terminated", {})
            if terminated:
                reason = terminated.get("reason", "")
                if reason in PROBLEMATIC_STATUSES:
                    return {
                        "name": pod_name,
                        "namespace": namespace,
                        "status": reason,
                        "message": terminated.get("message", ""),
                        "restart_count": cs.get("restartCount", 0),
                    }

        # Check pod phase
        if phase in ("Pending", "Failed", "Unknown"):
            return {
                "name": pod_name,
                "namespace": namespace,
                "status": phase,
                "message": status.get("reason", ""),
                "restart_count": 0,
            }

        return None


# Shared instance
pod_inspector = PodInspector()
