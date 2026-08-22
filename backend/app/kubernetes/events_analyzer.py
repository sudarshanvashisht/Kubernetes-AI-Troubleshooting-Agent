"""Kubernetes events analyzer.

Reads cluster events and detects warning-level events that indicate
potential issues such as FailedScheduling, BackOff, FailedMount, etc.
"""

import json
from typing import Any

from loguru import logger

from app.kubernetes.kubectl import kubectl


# Event reasons considered problematic
WARNING_REASONS = {
    "FailedScheduling",
    "BackOff",
    "FailedMount",
    "FailedAttachVolume",
    "FailedPull",
    "ErrImagePull",
    "Unhealthy",
    "FailedCreate",
    "FailedKillPod",
    "NodeNotReady",
    "Evicted",
    "OOMKilling",
    "InsufficientMemory",
    "InsufficientCPU",
}


class EventsAnalyzer:
    """Analyzes Kubernetes cluster events for issues."""

    async def analyze_events(
        self, namespace: str | None = None, context: str | None = None
    ) -> dict[str, Any]:
        """Analyze cluster events for warnings and issues.

        Args:
            namespace: Optional namespace filter. If None, checks all namespaces.
            context: Optional Kubernetes context.

        Returns:
            Dict with total event count, warning events, and issue flag.
        """
        cmd = "get events -o json"
        if namespace:
            cmd += f" -n {namespace}"
        else:
            cmd += " -A"

        result = await kubectl.run(cmd, context=context)

        if not result.success:
            logger.error(f"Failed to get events: {result.stderr}")
            return {
                "total_events": 0,
                "warning_events": [],
                "has_issues": False,
                "error": result.stderr,
            }

        try:
            events_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse events data: {e}")
            return {
                "total_events": 0,
                "warning_events": [],
                "has_issues": False,
                "error": f"Failed to parse kubectl output: {e}",
            }

        events = events_data.get("items", [])
        warning_events = []

        for event in events:
            event_info = self._check_event(event)
            if event_info:
                warning_events.append(event_info)

        has_issues = len(warning_events) > 0

        logger.info(
            f"Events analysis complete: {len(events)} total, "
            f"{len(warning_events)} warnings"
        )

        return {
            "total_events": len(events),
            "warning_events": warning_events,
            "has_issues": has_issues,
        }

    def _check_event(self, event: dict) -> dict | None:
        """Check if an event is a warning worth reporting.

        Returns event info dict if problematic, None otherwise.
        """
        event_type = event.get("type", "Normal")
        reason = event.get("reason", "")

        # Only interested in Warning events or known problematic reasons
        if event_type != "Warning" and reason not in WARNING_REASONS:
            return None

        involved_object = event.get("involvedObject", {})

        return {
            "reason": reason,
            "message": event.get("message", ""),
            "namespace": event.get("metadata", {}).get("namespace", ""),
            "involved_object": {
                "kind": involved_object.get("kind", ""),
                "name": involved_object.get("name", ""),
                "namespace": involved_object.get("namespace", ""),
            },
            "count": event.get("count", 1),
            "last_timestamp": event.get("lastTimestamp", ""),
        }


# Shared instance
events_analyzer = EventsAnalyzer()
