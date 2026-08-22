"""Network inspection utilities.

Inspects Kubernetes services and endpoints to detect networking
issues such as missing endpoints, selector mismatches, and
DNS-related problems.
"""

import json
from typing import Any

from loguru import logger

from app.kubernetes.kubectl import kubectl


class NetworkInspector:
    """Inspects service and network health across the Kubernetes cluster."""

    async def inspect_services(
        self, namespace: str | None = None, context: str | None = None
    ) -> dict[str, Any]:
        """Inspect services and their endpoints.

        Args:
            namespace: Optional namespace filter. If None, checks all namespaces.
            context: Optional Kubernetes context.

        Returns:
            Dict with total services count, problematic services, and issue flag.
        """
        ns_flag = f"-n {namespace}" if namespace else "-A"

        # Get services and endpoints
        svc_result = await kubectl.run(f"get svc {ns_flag} -o json", context=context)
        ep_result = await kubectl.run(f"get endpoints {ns_flag} -o json", context=context)

        if not svc_result.success:
            logger.error(f"Failed to get services: {svc_result.stderr}")
            return {
                "total_services": 0,
                "problematic_services": [],
                "has_issues": False,
                "error": svc_result.stderr,
            }

        try:
            services_data = json.loads(svc_result.stdout)
            endpoints_data = json.loads(ep_result.stdout) if ep_result.success else {"items": []}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse network data: {e}")
            return {
                "total_services": 0,
                "problematic_services": [],
                "has_issues": False,
                "error": f"Failed to parse kubectl output: {e}",
            }

        services = services_data.get("items", [])
        endpoints = endpoints_data.get("items", [])

        # Build endpoint lookup: namespace/name -> endpoint
        endpoint_map = {}
        for ep in endpoints:
            ep_meta = ep.get("metadata", {})
            key = f"{ep_meta.get('namespace', '')}/{ep_meta.get('name', '')}"
            endpoint_map[key] = ep

        problematic = []

        for svc in services:
            svc_info = self._check_service_health(svc, endpoint_map)
            if svc_info:
                problematic.append(svc_info)

        has_issues = len(problematic) > 0

        logger.info(
            f"Network inspection complete: {len(services)} services, "
            f"{len(problematic)} with issues"
        )

        return {
            "total_services": len(services),
            "problematic_services": problematic,
            "has_issues": has_issues,
        }

    def _check_service_health(
        self, service: dict, endpoint_map: dict
    ) -> dict | None:
        """Check if a service has networking issues.

        Returns service info dict if problematic, None if healthy.
        """
        metadata = service.get("metadata", {})
        spec = service.get("spec", {})

        name = metadata.get("name", "unknown")
        namespace = metadata.get("namespace", "default")
        svc_type = spec.get("type", "ClusterIP")
        selector = spec.get("selector", {})

        # Skip kubernetes system service
        if name == "kubernetes" and namespace == "default":
            return None

        # Skip headless services and ExternalName services
        if spec.get("clusterIP") == "None" or svc_type == "ExternalName":
            return None

        issues = []

        # Check for services with selectors but no endpoints
        if selector:
            key = f"{namespace}/{name}"
            endpoint = endpoint_map.get(key, {})
            subsets = endpoint.get("subsets", [])

            has_ready_addresses = False
            for subset in subsets:
                if subset.get("addresses"):
                    has_ready_addresses = True
                    break

            if not has_ready_addresses:
                issues.append("No ready endpoints found")

        # Check for services with no selector (potential misconfiguration)
        if not selector and svc_type != "ExternalName":
            issues.append("Service has no selector defined")

        if issues:
            return {
                "name": name,
                "namespace": namespace,
                "type": svc_type,
                "issues": issues,
            }

        return None


# Shared instance
network_inspector = NetworkInspector()
