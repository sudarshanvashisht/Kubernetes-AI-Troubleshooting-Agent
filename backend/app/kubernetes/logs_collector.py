"""Pod logs collector.

Fetches logs from failed or problematic pods for troubleshooting.
Keeps logs concise by limiting tail lines.
"""

from typing import Any

from loguru import logger

from app.kubernetes.kubectl import kubectl


class LogsCollector:
    """Collects logs from Kubernetes pods."""

    DEFAULT_TAIL_LINES = 50

    async def collect_logs(
        self, pod_name: str, namespace: str = "default", tail_lines: int | None = None, context: str | None = None
    ) -> dict[str, Any]:
        """Fetch logs for a specific pod.

        Args:
            pod_name: Name of the pod.
            namespace: Kubernetes namespace.
            tail_lines: Number of log lines to retrieve from the end.
            context: Optional Kubernetes context.

        Returns:
            Dict with pod name, namespace, and log content.
        """
        lines = tail_lines or self.DEFAULT_TAIL_LINES
        cmd = f"logs {pod_name} -n {namespace} --tail={lines}"

        result = await kubectl.run(cmd, context=context)

        if not result.success:
            logger.warning(f"Failed to get logs for {namespace}/{pod_name}: {result.stderr}")
            # Try getting logs from previous container instance
            cmd_prev = f"logs {pod_name} -n {namespace} --tail={lines} --previous"
            result_prev = await kubectl.run(cmd_prev, context=context)

            if result_prev.success:
                return {
                    "pod_name": pod_name,
                    "namespace": namespace,
                    "logs": result_prev.stdout,
                    "source": "previous_container",
                }

            return {
                "pod_name": pod_name,
                "namespace": namespace,
                "logs": "",
                "error": result.stderr,
            }

        return {
            "pod_name": pod_name,
            "namespace": namespace,
            "logs": result.stdout,
            "source": "current_container",
        }

    async def collect_failed_pod_logs(
        self, problematic_pods: list[dict], tail_lines: int | None = None, context: str | None = None
    ) -> list[dict[str, Any]]:
        """Collect logs for all problematic pods."""
        logs = []

        for pod in problematic_pods:
            pod_name = pod.get("name", "")
            namespace = pod.get("namespace", "default")

            if not pod_name:
                continue

            logger.info(f"Collecting logs for {namespace}/{pod_name}")
            log_entry = await self.collect_logs(pod_name, namespace, tail_lines, context=context)
            logs.append(log_entry)

        logger.info(f"Collected logs for {len(logs)} problematic pods")
        return logs


# Shared instance
logs_collector = LogsCollector()
